"""Bounded native-process acceptance checks for the selected GDAL backend."""
from __future__ import annotations

import numpy as np
import rasterio
from rasterio.transform import from_origin

from .gdal_viewshed import ViewshedSettings, generate_viewshed
from .runtime import PROJECT, Run, atomic_json, config, require_resources


def smoke_tests(run: Run, *, entry_available_ram_gib: float = 4) -> dict:
    marker = PROJECT/'data/processed/gdal_validation.json'
    report = {'run_id':run.id,'passed':False,'status':'running','cases':{},
              'entry_available_ram_gib':entry_available_ram_gib}
    atomic_json(marker,report)
    try:
        cfg=config()
        if not np.isfinite(entry_available_ram_gib) or entry_available_ram_gib < cfg['resources']['runtime_reserve_available_gib']:
            raise ValueError('Entry override must retain the runtime RAM reserve')
        cfg['resources']['pilot_entry_available_gib']=entry_available_ram_gib
        report['entry_resources']=require_resources(cfg,pilot=True)
        directory = PROJECT/'data/interim/gdal_smoke'/run.id
        directory.mkdir(parents=True,exist_ok=True)
        cases = [('flat',False,1.7,30,True,1),('ridge',True,1.7,30,True,0),
                 ('high_observer',True,300.0,30,True,1),
                 ('curvature_off',False,1.7,1000,False,1),
                 ('curvature_on',False,1.7,1000,True,0),
                 ('missing_terrain',False,1.7,30,True,None)]
        for name,ridge,height,cell,curvature,expected in cases:
            dem=directory/f'{name}.tif'
            output=directory/f'{name}_view.tif'
            a=np.full((241,241),100,dtype='float32')
            if ridge:a[:,120]=200
            if name=='missing_terrain':a[120,110]=-9999
            with rasterio.open(dem,'w',driver='GTiff',width=241,height=241,count=1,
                    dtype='float32',crs='EPSG:32642',transform=from_origin(500000,4650000,cell,cell),nodata=-9999) as ds:
                ds.write(a,1)
            observer=(500000+90.5*cell,4650000-120.5*cell)
            target=(500000+150.5*cell,observer[1])
            settings=ViewshedSettings(radius_m=2000 if cell==30 else 62000,
                                     observer_height_m=height,earth_curvature=curvature)
            try:
                result=generate_viewshed(dem,output,observer,settings=settings,
                                        entry_available_ram_gib=entry_available_ram_gib)
            except RuntimeError as error:
                if expected is not None or 'Missing terrain' not in str(error):raise
                case={'passed':not output.exists(),'expected':'NoData rejected before publication',
                      'observed':'NoData rejected before publication'}
            else:
                with rasterio.open(output) as ds:value=int(next(ds.sample([target]))[0])
                case={'passed':value==expected,'expected':expected,'observed':value,
                      'signature':result['signature'],'measurements':result['measurements']}
            report['cases'][name]=case
            run.event('gdal_synthetic_case',case=name,**case)
            atomic_json(marker,report)
        report.update(passed=all(c['passed'] for c in report['cases'].values()),status='complete')
        if not report['passed']:raise RuntimeError('GDAL synthetic acceptance failed')
    except BaseException as error:
        report.update(status='blocked_or_failed',passed=False,error=str(error))
        raise
    finally:
        atomic_json(marker,report)
    return report
