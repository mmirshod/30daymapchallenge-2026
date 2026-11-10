"""Isolated one-summit G4 worker; completed products have atomic checkpoints."""
from __future__ import annotations

import json
from pathlib import Path
import sys
import time

import geopandas as gpd

from .data_readiness import DEM,write_parquet
from .g3_benchmark import landmark_diagnostic
from .gdal_viewshed import ViewshedSettings,generate_viewshed
from .panorama import terrain_summary,peak_edges,skyline_and_los
from .runtime import PROJECT,Run,atomic_json,config,fingerprint,require_resources


def process_observer(request):
    observer=request['observer'];signature=request['signature']
    cfg=config()
    if cfg['analysis']!=request['analysis'] or cfg['landmarks']!=request['landmarks']:
        raise RuntimeError('Physical/landmark configuration changed during analysis')
    require_resources(cfg)
    directory=Path(request['directory']);directory.mkdir(parents=True,exist_ok=True)
    name=observer['observer_id'].replace(':','_')
    started=time.monotonic()
    with Run('g4-observer',{'observer_id':observer['observer_id'],'signature':signature}).capture() as run:
        targets=gpd.read_parquet(PROJECT/'data/processed/target_peaks.parquet')
        landmarks=gpd.read_parquet(PROJECT/'data/processed/landmarks_audited.parquet')
        output=directory/f'{name}_view.tif'
        view=generate_viewshed(DEM,output,(observer['x'],observer['y']),
            settings=ViewshedSettings(radius_m=cfg['analysis']['radius_m'],
                observer_height_m=cfg['analysis']['observer_height_m'],
                refraction_coefficient=cfg['analysis']['refraction_coefficient'],
                earth_curvature=cfg['analysis']['earth_curvature']),entry_available_ram_gib=1)
        adapter_seconds=time.monotonic()-started
        terrain=terrain_summary(output,{**cfg,'_observer_xy':(observer['x'],observer['y'])})
        peak_started=time.monotonic()
        edges,peaks=peak_edges(output,observer,targets,cfg)
        edges_path=directory/f'{name}_edges.parquet';write_parquet(edges,edges_path)
        peaks['wall_seconds']=time.monotonic()-peak_started
        horizon,los=skyline_and_los(DEM,output,observer,edges,cfg)
        horizon_path=directory/f'{name}_horizon.json';atomic_json(horizon_path,horizon)
        los_path=directory/f'{name}_los.json';atomic_json(los_path,los)
        artifacts=[output,output.with_suffix('.tif.json'),edges_path,horizon_path,los_path]
        result={'status':'complete','signature':signature,'observer':observer,'terrain':terrain,'peaks':peaks,
            'landmarks':landmark_diagnostic(output,observer,landmarks,cfg['analysis']['radius_m']),
            'skyline_diagnostics':horizon['diagnostic_metrics'],'los':{k:v for k,v in los.items() if k!='checks'},
            'timings':{'adapter_seconds':adapter_seconds,'terrain_seconds':terrain['wall_seconds'],
                'peak_seconds':peaks['wall_seconds'],'skyline_and_los_seconds':los['combined_skyline_los_wall_seconds'],
                'case_wall_seconds':time.monotonic()-started},
            'artifact_sha256':{str(p.relative_to(PROJECT)):fingerprint(p) for p in artifacts},
            'run_id':run.id,'lake_visibility_in_ranking':False,'mps_complete':False}
        # This marker is written last: partial observer work never counts as done.
        atomic_json(Path(request['marker']),result)
        run.event('observer_checkpoint_complete',case_wall_seconds=result['timings']['case_wall_seconds'])
    return result


if __name__=='__main__':
    process_observer(json.loads(Path(sys.argv[1]).read_text(encoding='utf-8')))
