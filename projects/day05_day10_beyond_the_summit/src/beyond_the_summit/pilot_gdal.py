"""Independent GDAL performance/algorithm cross-check; not a backend switch."""
from __future__ import annotations
import json
from pathlib import Path
import time
import numpy as np
import rasterio
from osgeo import gdal
from .pilot import crop_window,independent_profiles
from .runtime import PROJECT,Run,atomic_json,config,fingerprint,require_resources


def benchmark_gdal():
    cfg=config();require_resources(cfg,pilot=True)
    reference_path=PROJECT/'data/processed/pilot_100km30.json'
    if not reference_path.exists():raise RuntimeError('Finish GRASS resolution cases before independent engine check')
    reference=json.loads(reference_path.read_text(encoding='utf-8'));cases=[]
    directory=PROJECT/'data/interim/pilot_gdal';directory.mkdir(parents=True,exist_ok=True)
    gdal.UseExceptions();gdal.SetCacheMax(128*2**20)
    with rasterio.open(PROJECT/'data/interim/pilot_dem_30m.tif') as source:
        for prior in reference['cases']:
            require_resources(cfg,pilot=True,additional_disk_bytes=512*2**20)
            observer=prior['observer'];x,y=observer['x'],observer['y'];radius=100000
            with Run('pilot-gdal-observer',observer).capture() as run:
                dem=directory/f'{run.id}_dem.tif';raw=directory/f'{run.id}_raw.tif';output=directory/f'{run.id}_view.tif'
                a,tr=crop_window(source,x,y,radius)
                with rasterio.open(dem,'w',driver='GTiff',width=a.shape[1],height=a.shape[0],count=1,
                    dtype='float32',crs=source.crs,transform=tr,nodata=-9999,compress='deflate',tiled=True) as target:target.write(a,1)
                del a
                started=time.monotonic()
                def progress(fraction,message,data):
                    require_resources(cfg)
                    if time.monotonic()-started>120:raise TimeoutError('Independent GDAL case exceeded 2 minutes')
                    return 1
                ds=gdal.Open(str(dem))
                result=gdal.ViewshedGenerate(ds.GetRasterBand(1),'GTiff',str(raw),['COMPRESS=DEFLATE','TILED=YES'],
                    x,y,cfg['analysis']['observer_height_m'],0,1,0,255,255,
                    1-cfg['analysis']['refraction_coefficient'],gdal.GVM_Edge,radius+source.res[0],progress)
                if result is None:raise RuntimeError('GDAL viewshed failed')
                result=None;ds=None;seconds=time.monotonic()-started
                with rasterio.open(dem) as d:bounds=list(d.bounds)
                aligned=gdal.Warp(str(output),str(raw),format='GTiff',outputBounds=bounds,xRes=30,yRes=30,
                    resampleAlg='near',dstNodata=255,outputType=gdal.GDT_Byte,creationOptions=['COMPRESS=DEFLATE','TILED=YES'])
                aligned=None
                visible=total=agree=compared=0
                with rasterio.open(output) as current,rasterio.open(PROJECT/prior['output']) as grass:
                    for _,w in current.block_windows(1):
                        v=current.read(1,window=w);g=grass.read(1,window=w)
                        xx=current.transform.c+(w.col_off+np.arange(w.width)+.5)*30
                        yy=current.transform.f-(w.row_off+np.arange(w.height)+.5)*30
                        inside=np.hypot(xx[None,:]-x,yy[:,None]-y)<=radius
                        if np.any(inside&~np.isin(v,[0,1])):raise RuntimeError('GDAL output has unknown cells within circle')
                        visible+=int(np.sum(inside&(v==1)));total+=int(inside.sum())
                        valid=inside&np.isin(g,[0,1]);compared+=int(valid.sum());agree+=int(np.sum(valid&(v==g)))
                los=independent_profiles(dem,output,x,y,radius,observer_reference='cell')
                case={'observer':observer,'engine':'GDAL ViewshedGenerate GVM_Edge','gdal_version':gdal.VersionInfo(),
                    'compute_and_output_seconds':seconds,'visible_area_km2':visible*.0009,
                    'pixel_agreement_with_grass':agree/compared,'grass_visible_area_km2':prior['visible_area_km2'],
                    'cell_reference_los':los,'sampled_peak_process_tree_rss_bytes':run.peak_rss,
                    'output':str(output.relative_to(PROJECT)),'output_sha256':fingerprint(output),
                    'status':'independent pilot diagnostic; changing production backend requires review'}
                cases.append(case);run.event('gdal_case_complete',observer_id=observer['observer_id'],compute_seconds=seconds,
                    pixel_agreement=agree/compared)
                atomic_json(PROJECT/'data/processed/pilot_gdal.json',{'cases':cases,'production_backend_changed':False})
                dem.unlink();raw.unlink()
                print(f"GDAL {observer['observer_id']}: {seconds:.2f}s",flush=True)
    return {'cases':cases,'production_backend_changed':False}
