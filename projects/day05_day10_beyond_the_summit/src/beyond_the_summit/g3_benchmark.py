"""Twelve-observer end-to-end GDAL benchmark; never approves production."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import time

import geopandas as gpd
import numpy as np
import rasterio

from .data_readiness import DEM, write_parquet
from .gdal_viewshed import generate_viewshed, ViewshedSettings
from .panorama import terrain_summary, peak_edges, skyline_and_los
from .runtime import PROJECT, Run, atomic_json, config, fingerprint, require_resources


def checkpoint_valid(path, signature):
    try:
        data=json.loads(path.read_text(encoding='utf-8'))
        return (data['status']=='complete' and data['signature']==signature and
                all((PROJECT/name).exists() and fingerprint(PROJECT/name)==digest
                    for name,digest in data['artifact_sha256'].items()) and bool(data['artifact_sha256']))
    except (OSError,ValueError,KeyError):return False


def landmark_diagnostic(path,observer,landmarks,radius):
    # Exclude lakes before any visibility sampling, including diagnostics.
    distance=np.hypot(landmarks.geometry.x-observer['x'],landmarks.geometry.y-observer['y'])
    selected=landmarks[(distance<=radius)&~landmarks.excluded_from_ranking].copy()
    with rasterio.open(path) as view:
        values=[int(v[0]) for v in view.sample([(p.x,p.y) for p in selected.geometry])]
    return {'lake_records_sampled':0,'candidate_nonlake_landmarks':len(selected),
            'visible_ground_point_proxies':sum(v==1 for v in values),
            'unknown_points':sum(v not in (0,1) for v in values),
            'scoring_eligible_count':int(selected.scoring_eligible.sum()),
            'status':'diagnostic only; membership/visual eligibility unverified, no MPS score'}


def run_g3(run,*,entry_available_ram_gib=2):
    cfg=config()
    if not np.isfinite(entry_available_ram_gib) or entry_available_ram_gib<cfg['resources']['runtime_reserve_available_gib']:
        raise ValueError('G3 entry override cannot remove runtime reserves')
    cfg['resources']['pilot_entry_available_gib']=entry_available_ram_gib
    require_resources(cfg,pilot=True)
    from .validation import validate_artifacts
    readiness=validate_artifacts().get('g2',{})
    if not readiness.get('nps_data_ready'):raise RuntimeError('G3 requires current certified terrain and target catalogue')
    native=json.loads((PROJECT/'data/processed/gdal_validation.json').read_text(encoding='utf-8'))
    if not native['passed']:raise RuntimeError('GDAL native smoke acceptance required')
    selected=json.loads((PROJECT/'data/processed/pilot_observers.json').read_text(encoding='utf-8'))
    if len(selected)!=12 or len({s['observer_id'] for s in selected})!=12:
        raise ValueError('G3 requires the twelve saved unique pilot observers')
    specification={'dem_sha256':fingerprint(DEM),
        'targets_sha256':fingerprint(PROJECT/'data/processed/target_peaks.parquet'),
        'landmarks_sha256':fingerprint(PROJECT/'data/processed/landmarks_audited.parquet'),
        'config_sha256':fingerprint(PROJECT/'config/analysis.yaml'),
        'environment_sha256':fingerprint(PROJECT/'environment-win-64.lock.txt'),
        'algorithms':{n:fingerprint(Path(__file__).with_name(n)) for n in
            ['g3_benchmark.py','panorama.py','gdal_viewshed.py','gdal_worker.py','native.py','runtime.py','los.py']},
        'observers':selected,'skyline_step_degrees':.1,'radius_m':100000,'resolution_m':30}
    signature=hashlib.sha256(json.dumps(specification,sort_keys=True).encode()).hexdigest()
    directory=PROJECT/'data/interim/g3'/signature[:16];directory.mkdir(parents=True,exist_ok=True)
    targets=gpd.read_parquet(PROJECT/'data/processed/target_peaks.parquet')
    landmarks=gpd.read_parquet(PROJECT/'data/processed/landmarks_audited.parquet')
    cases=[];started=time.monotonic()
    report_path=PROJECT/'data/processed/g3_benchmark.json'
    atomic_json(report_path,{'status':'running','signature':signature,'cases':[], 'run_id':run.id})
    for index,observer in enumerate(selected):
        require_resources(cfg,pilot=True,additional_disk_bytes=512*2**20)
        if time.monotonic()-started>cfg['resources']['pilot_wall_seconds']:
            raise TimeoutError('G3 total time budget exceeded')
        name=observer['observer_id'].replace(':','_')
        marker=directory/f'{name}.json'
        if checkpoint_valid(marker,signature):
            case=json.loads(marker.read_text(encoding='utf-8'));case['reused']=True
            cases.append(case)
            print(f'G3 {index+1}/12 {name}: validated checkpoint reused',flush=True)
            continue
        print(f'G3 {index+1}/12 {name}: starting',flush=True)
        case_started=time.monotonic()
        with Run('g3-observer',{'observer_id':observer['observer_id'],'signature':signature}).capture() as observer_run:
            output=directory/f'{name}_view.tif'
            settings=ViewshedSettings(observer_height_m=cfg['analysis']['observer_height_m'],
                radius_m=cfg['analysis']['radius_m'],refraction_coefficient=cfg['analysis']['refraction_coefficient'],
                earth_curvature=cfg['analysis']['earth_curvature'])
            view=generate_viewshed(DEM,output,(observer['x'],observer['y']),settings=settings,
                                   entry_available_ram_gib=entry_available_ram_gib)
            native_seconds=time.monotonic()-case_started
            local_cfg={**cfg,'_observer_xy':(observer['x'],observer['y'])}
            terrain=terrain_summary(output,local_cfg)
            target_started=time.monotonic()
            edges,peaks=peak_edges(output,observer,targets,cfg)
            edges_path=directory/f'{name}_edges.parquet';write_parquet(edges,edges_path)
            peaks['wall_seconds']=time.monotonic()-target_started
            horizon,los=skyline_and_los(DEM,output,observer,edges,cfg)
            horizon_path=directory/f'{name}_horizon.json';atomic_json(horizon_path,horizon)
            los_path=directory/f'{name}_los.json';atomic_json(los_path,los)
            landmark=landmark_diagnostic(output,observer,landmarks,cfg['analysis']['radius_m'])
            artifacts=[output,output.with_suffix('.tif.json'),edges_path,horizon_path,los_path]
            case={'status':'complete','signature':signature,'observer':observer,'reused':False,
                'view_reused':view['reused'],'terrain':terrain,'peaks':peaks,'landmarks':landmark,
                'skyline_diagnostics':horizon['diagnostic_metrics'],
                'los':{k:v for k,v in los.items() if k!='checks'},
                'timings':{'gdal_compute_initial_output_seconds':view['details']['compute_and_initial_output_seconds'],
                    'adapter_total_seconds':native_seconds,'terrain_summary_seconds':terrain['wall_seconds'],
                    'target_summary_seconds':peaks['wall_seconds'],
                    'skyline_seconds':horizon['wall_seconds'],
                    'skyline_and_los_seconds':los['combined_skyline_los_wall_seconds'],
                    'case_wall_seconds':time.monotonic()-case_started},
                'native_measurements':view['measurements'],
                'artifact_sha256':{str(p.relative_to(PROJECT)):fingerprint(p) for p in artifacts},
                'observer_run_id':observer_run.id,'horizon':str(horizon_path.relative_to(PROJECT))}
            atomic_json(marker,case)
            observer_run.event('case_complete',case_wall_seconds=case['timings']['case_wall_seconds'])
        cases.append(case)
        atomic_json(report_path,{'status':'running','signature':signature,'cases':cases,'run_id':run.id})
        print(f"G3 {index+1}/12: {case['timings']['case_wall_seconds']:.2f}s; {peaks['visible_peak_ground_proxies']} visible peak proxies",flush=True)
    all_checks=[c['los'] for c in cases]
    total=sum(c['count'] for c in all_checks);ng=sum(c['non_grazing_count'] for c in all_checks)
    times=np.array([c['timings']['case_wall_seconds'] for c in cases if not c['view_reused']])
    result={'status':'complete','run_id':run.id,'signature':signature,'specification':specification,
        'cases':cases,'case_count':len(cases),'resumed_cases':sum(c['reused'] for c in cases),
        'invocation_wall_seconds':time.monotonic()-started,
        'los_count':total,'non_grazing_los_count':ng,
        'non_grazing_los_agreement':sum((c['non_grazing_agreement_fraction'] or 0)*c['non_grazing_count'] for c in all_checks)/ng if ng else None,
        'full_cohort_estimate':{'basis':'original fresh observer-case measurements, retained on resume; includes adapter, terrain, peaks, skyline and LOS; excludes publication, retries and cohort startup',
            'fresh_case_count':len(times),'median_case_seconds':float(np.median(times)) if len(times) else None,
            'median_scaled_hours':float(np.median(times)*1302/3600) if len(times) else None,
            'min_max_scaled_hours':[float(times.min()*1302/3600),float(times.max()*1302/3600)] if len(times) else None},
        'lake_visibility_in_ranking':False,'mps_complete':False,'production_approved':False,
        'quality':'exploratory benchmark; LOS disagreements remain diagnostic; no rankings produced'}
    atomic_json(report_path,result)
    return {k:v for k,v in result.items() if k not in ('cases','specification')}
