from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile

import numpy as np
import rasterio
from rasterio.transform import from_origin

from .native import grass_command
from .runtime import PROJECT, Run, atomic_json, config, fingerprint


def viewshed(dem: Path, output: Path, coordinates: tuple[float,float], *,
             observer_height_m: float=1.7, radius_m: float=2000,
             flags: str='bcr', memory_mb: int=64, timeout: float=120) -> dict:
    with rasterio.open(dem) as source:
        cell_size=max(source.res)
        if source.crs is None or not source.crs.is_projected or abs(source.crs.linear_units_factor[1]-1)>1e-8:
            raise ValueError('Viewshed requires a projected metric DEM')
        x,y=coordinates
        if not (source.bounds.left<=x<source.bounds.right and source.bounds.bottom<y<=source.bounds.top):
            raise ValueError('Observer outside DEM coverage')
        for _,window in source.block_windows(1):
            values=source.read(1,window=window,masked=True)
            invalid=np.ma.getmaskarray(values)|~np.isfinite(values.filled(np.nan))
            if invalid.any():
                rr,cc=np.where(invalid)
                xs=source.transform.c+(window.col_off+cc+.5)*source.res[0]
                ys=source.transform.f-(window.row_off+rr+.5)*source.res[1]
                if np.any(np.hypot(xs-x,ys-y)<=radius_m+2*max(source.res)):
                    raise ValueError('Viewshed input contains missing terrain within circle/halo; no silent NoData substitution')
    request={'dem':str(dem),'output':str(output),'coordinates':list(coordinates),
             'observer_height_m':observer_height_m,'analysis_radius_m':radius_m,'radius_m':radius_m+cell_size,
             'refraction_coefficient':0.14286,'flags':flags,'memory_mb':memory_mb}
    request_path=output.with_suffix('.request.json');atomic_json(request_path,request)
    # GRASS 8.5's classic first-run startup checks for a prior rc/mapset even
    # with --tmp-project. An explicitly named, disposable project avoids that
    # upstream first-run path and still gives every worker an isolated mapset.
    temporary_root=PROJECT.parents[1]/'.bts/tmp'
    temporary_root.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='grass_',dir=temporary_root) as directory:
        result=grass_command(['--text','-c','EPSG:32642',str(Path(directory)/'project'),
                              '--exec',sys.executable,
                              str(Path(__file__).with_name('grass_worker.py')),str(request_path)],timeout=timeout)
    output.with_suffix('.stderr.txt').write_text(result.stderr,encoding='utf-8')
    return {**request,'measurements':result.measurements}


def native_smoke_tests(run: Run) -> dict:
    directory=PROJECT/'data/interim/native_smoke'/run.id;directory.mkdir(parents=True,exist_ok=True)
    atomic_json(PROJECT/'data/processed/native_validation.json',{'passed':False,'status':'running','run_id':run.id})
    transform=from_origin(500000,4650000,30,30)
    coordinates=(500000+5.5*30,4650000-20.5*30)
    tests={}
    for case,height in [('flat',1.7),('ridge',1.7),('ridge_high_observer',300.0)]:
        terrain=np.full((41,41),100,dtype='float32')
        if case.startswith('ridge'):
            terrain[:,20]=200
        dem=directory/f'{case}.tif';output=directory/f'{case}_viewshed.tif'
        with rasterio.open(dem,'w',driver='GTiff',width=41,height=41,count=1,dtype='float32',
                           crs='EPSG:32642',transform=transform,nodata=-9999) as ds:
            ds.write(terrain,1)
        request=viewshed(dem,output,coordinates,observer_height_m=height)
        with rasterio.open(output) as ds:
            xy=(500000+35.5*30,4650000-20.5*30)
            value=int(next(ds.sample([xy]))[0])
        expected=0 if case=='ridge' else 1
        tests[case]={'expected':expected,'observed':value,'passed':value==expected,'request':request}
        run.event('synthetic_case',case=case,passed=value==expected)
    terrain=np.full((81,81),100,dtype='float32')
    dem=directory/'curved_flat.tif'
    with rasterio.open(dem,'w',driver='GTiff',width=81,height=81,count=1,dtype='float32',
                       crs='EPSG:32642',transform=from_origin(500000,4650000,1000,1000),nodata=-9999) as ds:
        ds.write(terrain,1)
    for case,flags,expected in [('curvature_off','b',1),('curvature_refraction_on','bcr',0)]:
        output=directory/f'{case}.tif'
        request=viewshed(dem,output,(520500,4609500),radius_m=60000,flags=flags)
        with rasterio.open(output) as ds:
            value=int(next(ds.sample([(560500,4609500)]))[0])
        tests[case]={'expected':expected,'observed':value,'passed':value==expected,'request':request}
        run.event('synthetic_case',case=case,passed=value==expected)
    report={'tests':tests,'passed':all(t['passed'] for t in tests.values()),'run_id':run.id,
            'limitations':'Synthetic backend checks only; real-terrain LOS and pilot convergence checks remain required.'}
    atomic_json(PROJECT/'data/processed/native_validation.json',report)
    if not report['passed']:
        raise RuntimeError('Native synthetic visibility validation failed')
    return report


def validate_artifacts() -> dict:
    checks={}
    for name in ['preparation.json','environment.json','native_validation.json','gdal_validation.json']:
        p=PROJECT/'data/processed'/name
        checks[name]={'exists':p.exists(),'sha256':fingerprint(p) if p.exists() else None}
    prep=PROJECT/'data/processed/preparation.json'
    if prep.exists():
        d=json.loads(prep.read_text(encoding='utf-8'))
        checks['candidate_count']={'passed':d['observer_count']==config()['study']['expected_observers']}
        checks['full_data_readiness']={'passed':d['cross_border_dem_validated'] and d['landmark_registry_validated']}
    pilots={}
    for phase in ['local','100km','100km30']:
        path=PROJECT/f'data/processed/pilot_{phase}.json'
        if path.exists():
            data=json.loads(path.read_text(encoding='utf-8'));pilots[phase]={'cases':len(data['cases']),'radius_m':data['radius_m']}
    result={'checks':checks,'terrain_pilots':pilots,'production_ready':False,
            'note':'Terrain pilot measurements do not establish catalogue completeness, rankings or production approval.'}
    readiness=PROJECT/'data/processed/g2_readiness.json'
    if readiness.exists():
        g2=json.loads(readiness.read_text(encoding='utf-8'))
        checksums={**g2.get('artifact_sha256',{}),**g2.get('source_sha256',{})}
        current=bool(checksums) and all((PROJECT/name).exists() and fingerprint(PROJECT/name)==digest
                                      for name,digest in checksums.items())
        current=current and g2.get('config_sha256')==fingerprint(PROJECT/'config/analysis.yaml')
        current=current and g2.get('environment_sha256')==fingerprint(PROJECT/'environment-win-64.lock.txt')
        current=current and g2.get('algorithm_sha256')==fingerprint(Path(__file__).with_name('data_readiness.py'))
        result['g2']={'artifact_fingerprints_valid':current,'terrain_ready':current and g2['terrain_ready'],
                      'target_catalogue_ready':current and g2['target_catalogue_ready'],
                      'nps_data_ready':current and g2['nps_data_ready'],'mps_data_ready':current and g2['mps_data_ready']}
    g3_path=PROJECT/'data/processed/g3_benchmark.json'
    if g3_path.exists():
        g3=json.loads(g3_path.read_text(encoding='utf-8'))
        spec=g3.get('specification',{})
        valid=g3.get('status')=='complete' and g3.get('case_count')==12
        valid=valid and spec.get('config_sha256')==fingerprint(PROJECT/'config/analysis.yaml')
        valid=valid and spec.get('environment_sha256')==fingerprint(PROJECT/'environment-win-64.lock.txt')
        valid=valid and all(spec.get(key)==fingerprint(PROJECT/name) for key,name in [
            ('dem_sha256','data/interim/pilot_dem_30m.tif'),
            ('targets_sha256','data/processed/target_peaks.parquet'),
            ('landmarks_sha256','data/processed/landmarks_audited.parquet')])
        valid=valid and all(fingerprint(Path(__file__).with_name(name))==digest for name,digest in spec.get('algorithms',{}).items())
        valid=valid and all((PROJECT/name).exists() and fingerprint(PROJECT/name)==digest
                           for case in g3.get('cases',[]) for name,digest in case['artifact_sha256'].items())
        result['g3']={'passed':bool(valid),'completed_cases':g3.get('case_count',0),
                      'lake_records_sampled':sum(c['landmarks']['lake_records_sampled'] for c in g3.get('cases',[])),
                      'rankings_computed':False,'production_approved':False}
    atomic_json(PROJECT/'data/processed/validation.json',result)
    return result

