import json
from copy import deepcopy

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
from rasterio.transform import from_origin
from shapely.geometry import Point

from beyond_the_summit import panorama,g3_benchmark
from beyond_the_summit.runtime import config,fingerprint


def fixture(tmp_path):
    transform=from_origin(500000,4650000,10,10)
    x,y=500605,4649395
    a=np.full((121,121),100,dtype='float32')
    rr,cc=np.indices(a.shape)
    inside=np.hypot((cc+.5)*10-605,605-(rr+.5)*10)<=500
    view=np.where(inside,1,255).astype('uint8')
    for name,values,nodata in [('dem',a,-9999),('view',view,255)]:
        with rasterio.open(tmp_path/f'{name}.tif','w',driver='GTiff',width=121,height=121,count=1,
            dtype=str(values.dtype),crs=32642,transform=transform,nodata=nodata) as ds:ds.write(values,1)
    cfg=deepcopy(config());cfg['analysis']['radius_m']=500
    cfg['analysis']['distance_bands_m']=[0,100,300,500];cfg['_observer_xy']=(x,y)
    observer={'x':x,'y':y,'observer_id':'self'}
    targets=gpd.GeoDataFrame({'target_id':['self','other','outside'],
        'elevation_m':[2000,2100,2200],'ground_dem_m':[100,100,100]},
        geometry=[Point(x,y),Point(x+200,y),Point(x+600,y)],crs=32642)
    return cfg,observer,targets,inside


def test_terrain_area_and_peak_self_exclusion(tmp_path,monkeypatch):
    monkeypatch.setattr(panorama,'require_resources',lambda *a,**k:None)
    cfg,observer,targets,inside=fixture(tmp_path)
    terrain=panorama.terrain_summary(tmp_path/'view.tif',cfg)
    assert terrain['visible_cells']==int(inside.sum())
    assert np.isclose(terrain['visible_area_km2'],inside.sum()*.0001)
    assert sum(b['cells'] for b in terrain['distance_bands'])==terrain['circle_cells']
    edges,stats=panorama.peak_edges(tmp_path/'view.tif',observer,targets,cfg)
    assert list(edges.target_id)==['other']
    assert stats['visible_peak_ground_proxies']==1
    assert 89<edges.iloc[0].bearing_true_degrees<91


def test_signed_skyline_and_independent_cell_reference(tmp_path,monkeypatch):
    monkeypatch.setattr(panorama,'require_resources',lambda *a,**k:None)
    cfg,observer,targets,_=fixture(tmp_path)
    edges,_=panorama.peak_edges(tmp_path/'view.tif',observer,targets,cfg)
    horizon,los=panorama.skyline_and_los(tmp_path/'dem.tif',tmp_path/'view.tif',observer,edges,cfg,step_degrees=10)
    assert len(horizon['horizon_degrees'])==36
    assert all(v<0 for v in horizon['horizon_degrees'])
    assert np.allclose(horizon['limiting_distance_projected_m'],500)
    assert all(0<=v<360 for v in horizon['azimuth_true_degrees'])
    assert los['count']==1 and los['agreement_fraction']==1


def test_lakes_are_not_sampled(tmp_path):
    cfg,observer,_,_=fixture(tmp_path)
    landmarks=gpd.GeoDataFrame({'excluded_from_ranking':[True,False],'scoring_eligible':[False,False]},
        geometry=[Point(observer['x'],observer['y']),Point(observer['x']+100,observer['y'])],crs=32642)
    result=g3_benchmark.landmark_diagnostic(tmp_path/'view.tif',observer,landmarks,500)
    assert result['lake_records_sampled']==0
    assert result['candidate_nonlake_landmarks']==1
    assert result['visible_ground_point_proxies']==1


def test_resume_rejects_interrupted_stale_or_corrupted_artifacts(tmp_path,monkeypatch):
    monkeypatch.setattr(g3_benchmark,'PROJECT',tmp_path)
    artifact=tmp_path/'data.bin';artifact.write_bytes(b'complete')
    marker=tmp_path/'case.json'
    record={'status':'complete','signature':'approved','artifact_sha256':{'data.bin':fingerprint(artifact)}}
    marker.write_text(json.dumps(record),encoding='utf-8')
    assert g3_benchmark.checkpoint_valid(marker,'approved')
    assert not g3_benchmark.checkpoint_valid(marker,'stale')
    artifact.write_bytes(b'interrupted')
    assert not g3_benchmark.checkpoint_valid(marker,'approved')
    record['status']='running';record['artifact_sha256']['data.bin']=fingerprint(artifact)
    marker.write_text(json.dumps(record),encoding='utf-8')
    assert not g3_benchmark.checkpoint_valid(marker,'approved')
