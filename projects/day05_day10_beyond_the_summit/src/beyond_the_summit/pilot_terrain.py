"""Build bounded-memory pilot mosaics from verified cached GLO-30 tiles."""
from __future__ import annotations
import json
import math
from pathlib import Path
import time
import geopandas as gpd
from osgeo import gdal
from .runtime import PROJECT,REPOSITORY,Run,atomic_json,config,fingerprint,require_resources


def build_pilot_terrain(resolution: int=90) -> dict:
    if resolution not in [30,90]:raise ValueError('Pilot resolution must be 30 or 90 m')
    cfg=config();require_resources(cfg,pilot=True,additional_disk_bytes=2*2**30)
    source=json.loads((PROJECT/'data/processed/source_manifest.json').read_text(encoding='utf-8'))
    domain=next(d for d in source['domains'] if d['radius_m']==100000)
    paths=[];inputs=[]
    for tile in domain['tiles']:
        path=REPOSITORY/tile['cached_path'] if tile['cached_path'] else PROJECT/'data/raw/dem'/f"{tile['id']}.tif"
        if not path.exists():raise RuntimeError(f"Missing pilot terrain tile {tile['id']}")
        checksum=fingerprint(path)
        if not tile['cached_path']:
            meta=json.loads(path.with_suffix('.tif.download.json').read_text(encoding='utf-8'))
            if checksum!=meta['sha256'] or path.stat().st_size!=meta['expected_bytes']:
                raise RuntimeError('Downloaded tile verification failed')
        paths.append(str(path));inputs.append({'id':tile['id'],'sha256':checksum,'bytes':path.stat().st_size})
    points=gpd.read_parquet(PROJECT/'data/processed/observers.parquet')
    left,bottom,right,top=points.total_bounds;pad=100000+360
    bounds=[math.floor((left-pad)/90)*90,math.floor((bottom-pad)/90)*90,
            math.ceil((right+pad)/90)*90,math.ceil((top+pad)/90)*90]
    output=PROJECT/f'data/interim/pilot_dem_{resolution}m.tif'
    manifest_path=output.with_suffix('.manifest.json')
    specification={'inputs':inputs,'resolution_m':resolution,'bounds':bounds,'resampling':'bilinear',
                   'crs':cfg['analysis']['crs'],'source_product':'Copernicus GLO-30; 90 m is derived, not GLO-90'}
    if output.exists() and manifest_path.exists():
        previous=json.loads(manifest_path.read_text(encoding='utf-8'))
        if previous.get('specification')==specification and previous.get('sha256')==fingerprint(output):return previous
        raise RuntimeError('Existing pilot mosaic differs; preserve it and review configuration')
    gdal.UseExceptions();gdal.SetCacheMax(128*2**20)
    output.parent.mkdir(parents=True,exist_ok=True)
    started=time.monotonic()
    with Run('pilot-terrain',{'resolution_m':resolution,'source_tiles':len(paths)}).capture() as run:
        vrt_path=PROJECT/'data/interim/pilot_sources.vrt'
        vrt=gdal.BuildVRT(str(vrt_path),paths,options=gdal.BuildVRTOptions(resolution='highest',VRTNodata=-9999))
        vrt=None
        temporary=output.with_suffix('.partial.tif')
        def progress(fraction,message,data):
            require_resources(cfg,pilot=False)
            if time.monotonic()-started>600:raise TimeoutError('Terrain preparation exceeded 10 minutes')
            return 1
        dataset=gdal.Warp(str(temporary),str(vrt_path),format='GTiff',dstSRS=cfg['analysis']['crs'],
            outputBounds=bounds,xRes=resolution,yRes=resolution,resampleAlg='bilinear',
            dstNodata=-9999,outputType=gdal.GDT_Float32,warpMemoryLimit=64*2**20,multithread=False,
            creationOptions=['COMPRESS=DEFLATE','PREDICTOR=3','TILED=YES','BLOCKXSIZE=256','BLOCKYSIZE=256'],
            callback=progress)
        if dataset is None:raise RuntimeError('Pilot mosaic creation failed')
        shape=[dataset.RasterYSize,dataset.RasterXSize];dataset=None;temporary.replace(output)
        result={'specification':specification,'sha256':fingerprint(output),'shape':shape,
                'bytes':output.stat().st_size,'wall_seconds':time.monotonic()-started,
                'coverage_status':'per-observer circle plus interpolation halo must pass before computation'}
        atomic_json(manifest_path,result);run.event('mosaic_complete',**{k:v for k,v in result.items() if k!='specification'})
        return result
