"""Bounded sequential terrain benchmarks; never produce rankings."""
from __future__ import annotations
import hashlib
import json
import math
from pathlib import Path
import time
import numpy as np
import rasterio
from rasterio.windows import Window,from_bounds
from scipy.ndimage import map_coordinates
from .los import profile_visibility
from .runtime import PROJECT,REPOSITORY,Run,atomic_json,fingerprint,require_resources
from .validation import viewshed


def crop_window(source,x,y,radius):
    halo=2*max(source.res)
    raw=from_bounds(x-radius-halo,y-radius-halo,x+radius+halo,y+radius+halo,source.transform)
    left=math.floor(raw.col_off);top=math.floor(raw.row_off)
    right=math.ceil(raw.col_off+raw.width);bottom=math.ceil(raw.row_off+raw.height)
    if left<0 or top<0 or right>source.width or bottom>source.height:
        raise ValueError('Pilot circle plus interpolation halo is outside local DEM')
    window=Window(left,top,right-left,bottom-top)
    a=source.read(1,window=window,masked=True)
    invalid=np.ma.getmaskarray(a)|~np.isfinite(a.filled(np.nan))
    if invalid.any():
        rr,cc=np.where(invalid);tr=source.window_transform(window)
        xs=tr.c+(cc+.5)*source.res[0];ys=tr.f-(rr+.5)*source.res[1]
        if np.any(np.hypot(xs-x,ys-y)<=radius+halo):
            raise ValueError('Pilot circle/halo contains missing terrain')
    return np.asarray(a.filled(-9999),dtype='float32'),source.window_transform(window)


def independent_profiles(dem,output,x,y,radius,*,count=72,seed=20261109,k=.14286,observer_reference='point'):
    """Diagnostic same-DSM rays, stratified by native class and distance."""
    with rasterio.open(dem) as terrain,rasterio.open(output) as view:
        a=terrain.read(1);v=view.read(1);res=terrain.res[0]
        original_x,original_y=x,y
        if observer_reference=='cell':
            row,col=terrain.index(x,y);x,y=terrain.xy(row,col)
        elif observer_reference!='point':raise ValueError('Unknown observer reference')
        # Uniform random priorities give a fixed-size reservoir per native
        # class/range stratum, with only a 128-row coordinate block in memory.
        rng=np.random.default_rng(seed);reservoirs={}
        xs=terrain.transform.c+(np.arange(v.shape[1])+.5)*res
        per=max(1,count//6)
        for start in range(0,v.shape[0],128):
            stop=min(start+128,v.shape[0]);ys=terrain.transform.f-(np.arange(start,stop)+.5)*res
            distance=np.hypot(xs[None,:]-x,ys[:,None]-y)
            for band,(lo,hi) in enumerate([(3*res,radius/3),(radius/3,2*radius/3),(2*radius/3,radius)]):
                for visible in [0,1]:
                    rr,cc=np.where((distance>lo)&(distance<=hi)&(v[start:stop]==visible))
                    if not len(rr):continue
                    priorities=rng.random(len(rr));keep=np.argpartition(priorities,min(per,len(rr))-1)[:per]
                    entries=reservoirs.get((band,visible),[])+[(float(priorities[i]),int(rr[i]+start),int(cc[i])) for i in keep]
                    reservoirs[(band,visible)]=sorted(entries)[:per]
        chosen=[(r,c) for key in sorted(reservoirs) for _,r,c in reservoirs[key]]
        inverse=~terrain.transform;results=[]
        for row,col in chosen:
            tx=float(xs[col]);ty=float(terrain.transform.f-(row+.5)*res);length=float(math.hypot(tx-x,ty-y))
            d=np.linspace(0,length,max(3,math.ceil(length/(res/2))+1))
            px=x+(tx-x)*d/length;py=y+(ty-y)*d/length
            columns=inverse.a*px+inverse.b*py+inverse.c-.5
            r=inverse.d*px+inverse.e*py+inverse.f-.5
            ground=map_coordinates(a,[r,columns],order=1,mode='nearest',prefilter=False)
            independent=profile_visibility(d,ground,refraction_coefficient=k,
                earth_radius_m=6378137.0 if observer_reference=='cell' else 6371008.8)
            expected=bool(v[row,col]);clearance=independent['minimum_clearance_m']
            results.append({'target_x':tx,'target_y':ty,'distance_m':length,
                'grass_visible':expected,'profile_visible':independent['visible'],
                'minimum_profile_clearance_m':clearance,'near_grazing_2m':abs(clearance)<=2,
                'agrees':expected==independent['visible']})
    non_grazing=[r for r in results if not r['near_grazing_2m']]
    return {'profiles':results,'count':len(results),'agreement_fraction':sum(r['agrees'] for r in results)/len(results) if results else None,
            'non_grazing_count':len(non_grazing),'non_grazing_agreement_fraction':sum(r['agrees'] for r in non_grazing)/len(non_grazing) if non_grazing else None,
            'observer_reference':observer_reference,'observer_reference_offset_m':math.hypot(x-original_x,y-original_y),
            'method':'bilinear DEM rays at <=half-cell spacing; point reference uses mean Earth radius; cell reference uses WGS84 semimajor axis to match GRASS',
            'limitations':'Same DSM is not ground truth; interpolation/curvature differ; 2 m grazing band is diagnostic.'}


def run_pilot(cfg,*,phase='local'):
    native=PROJECT/'data/processed/native_validation.json'
    if not native.exists() or not json.loads(native.read_text(encoding='utf-8'))['passed']:
        raise RuntimeError('Pilot gate: native synthetic validation has not passed')
    if phase not in ['local','100km','100km30']:raise ValueError('Unknown pilot phase')
    if phase in ['100km','100km30']:
        source_path=PROJECT/f"data/interim/pilot_dem_{30 if phase=='100km30' else 90}m.tif";radius=100000;number=3 if phase=='100km30' else 12
        if not source_path.exists():raise RuntimeError('Pilot gate: complete 100 km DEM not prepared')
    else:source_path=REPOSITORY/cfg['study']['dem_file'];radius=10000;number=3
    sample=json.loads((PROJECT/'data/processed/pilot_observers.json').read_text(encoding='utf-8'))
    signature={'source_sha256':fingerprint(source_path),'phase':phase,
               'observer_height_m':cfg['analysis']['observer_height_m'],
               'refraction_coefficient':cfg['analysis']['refraction_coefficient'],'version':3,
               'config_sha256':fingerprint(PROJECT/'config/analysis.yaml'),
               'environment_lock_sha256':fingerprint(PROJECT/'environment-win-64.lock.txt'),
               'algorithm_sha256':hashlib.sha256(''.join(fingerprint(Path(__file__).with_name(n)) for n in
                   ['pilot.py','validation.py','native.py','grass_worker.py','los.py','skyline.py']).encode()).hexdigest()}
    key=hashlib.sha256(json.dumps(signature,sort_keys=True).encode()).hexdigest()[:12]
    directory=PROJECT/'data/interim/pilot'/key;directory.mkdir(parents=True,exist_ok=True)
    selected=[];skipped=[]
    with rasterio.open(source_path) as source:
        if phase=='local':
            for tercile in [1,2,3]:
                for observer in [r for r in sample if r['elevation_tercile']==tercile]:
                    try:crop_window(source,observer['x'],observer['y'],radius)
                    except ValueError as error:skipped.append({'id':observer['observer_id'],'reason':str(error)});continue
                    selected.append(observer);break
        elif phase=='100km30':selected=[next(r for r in sample if r['elevation_tercile']==i) for i in [1,2,3]]
        else:selected=sample[:number]
    if len(selected)!=number:raise RuntimeError('Not enough complete pilot windows in the saved sample')
    started=time.monotonic();cases=[]
    with rasterio.open(source_path) as source:
        for observer in selected:
            require_resources(cfg,pilot=True,additional_disk_bytes=512*2**20)
            if time.monotonic()-started>min(900 if phase=='local' else cfg['resources']['pilot_wall_seconds'],cfg['resources']['pilot_wall_seconds']):
                raise TimeoutError('Pilot phase budget exhausted; completed checkpoints retained')
            ident=observer['observer_id'].replace(':','_');checkpoint=directory/f'{ident}.json'
            if checkpoint.exists():
                completed=json.loads(checkpoint.read_text(encoding='utf-8'))
                output=PROJECT/completed.get('output','missing')
                if completed.get('signature')==signature and completed.get('complete') and output.is_file() and fingerprint(output)==completed['output_sha256']:
                    cases.append(completed);continue
            with Run('pilot-observer',{'phase':phase,**observer,'radius_m':radius}).capture() as run:
                dem=directory/f'{ident}_dem.tif'
                a,transform=crop_window(source,observer['x'],observer['y'],radius)
                with rasterio.open(dem,'w',driver='GTiff',width=a.shape[1],height=a.shape[0],count=1,
                                   dtype='float32',crs=source.crs,transform=transform,nodata=-9999,
                                   compress='deflate',tiled=True) as target:target.write(a,1)
                del a
                output=directory/f'{ident}_{run.id[:8]}_view.tif'
                timing=viewshed(dem,output,(observer['x'],observer['y']),radius_m=radius,
                    observer_height_m=cfg['analysis']['observer_height_m'],
                    memory_mb=cfg['resources']['grass_memory_mb'],timeout=900)
                with rasterio.open(output) as view:
                    visible=valid=0;cell_area=view.res[0]*view.res[1]
                    for _,window in view.block_windows(1):
                        v=view.read(1,window=window)
                        xx=view.transform.c+(window.col_off+np.arange(window.width)+.5)*view.res[0]
                        yy=view.transform.f-(window.row_off+np.arange(window.height)+.5)*view.res[1]
                        inside=np.hypot(xx[None,:]-observer['x'],yy[:,None]-observer['y'])<=radius
                        if np.any(inside&~np.isin(v,[0,1])):raise ValueError('Unknown native visibility inside pilot circle')
                        visible+=int(np.sum((v==1)&inside));valid+=int(inside.sum())
                del v,xx,yy,inside
                comparisons=independent_profiles(dem,output,observer['x'],observer['y'],radius,k=cfg['analysis']['refraction_coefficient'])
                cell_comparisons=independent_profiles(dem,output,observer['x'],observer['y'],radius,
                    k=cfg['analysis']['refraction_coefficient'],observer_reference='cell') if phase=='100km30' else None
                horizons={}
                if phase=='100km30':
                    from .skyline import horizon_profile
                    for step in [.25,.1,.05]:
                        profile=horizon_profile(dem,observer['x'],observer['y'],radius,step,
                            observer_height=cfg['analysis']['observer_height_m'],k=cfg['analysis']['refraction_coefficient'])
                        artifact=directory/f'{ident}_horizon_{step}.json';atomic_json(artifact,profile)
                        horizons[str(step)]={'wall_seconds':profile['wall_seconds'],'path':str(artifact.relative_to(PROJECT))}
                stages=json.loads(output.with_suffix('.stages.json').read_text(encoding='utf-8'))
                completed={'signature':signature,'complete':True,'run_id':run.id,'observer':observer,'radius_m':radius,
                    'resolution_m':source.res[0],'visible_cells':visible,'circle_cells':valid,
                    'visible_area_km2':visible*cell_area/1e6,'visible_fraction':visible/valid,
                    'timing':timing['measurements'],'stages':stages,'los':comparisons,
                    'los_cell_reference':cell_comparisons,'horizons':horizons,
                    'output':str(output.relative_to(PROJECT)),'output_sha256':fingerprint(output),
                    'input_window_bytes':dem.stat().st_size,'output_bytes':output.stat().st_size,
                    'sampled_full_case_peak_process_tree_rss_bytes':run.peak_rss}
                atomic_json(checkpoint,completed);cases.append(completed)
                run.event('case_complete',observer_id=observer['observer_id'],stages=stages,
                          visible_fraction=visible/valid,los_agreement=comparisons['agreement_fraction'])
                dem.unlink()
                print(f"Completed {phase} {observer['observer_id']}: {stages['viewshed_seconds']:.2f}s viewshed",flush=True)
    report={'phase':phase,'scope':'terrain viewshed benchmark only; no rankings','signature':signature,
            'radius_m':radius,'cases':cases,'selection_skips':skipped,
            'wall_seconds_this_invocation':time.monotonic()-started,
            'los_profiles':sum(c['los']['count'] for c in cases),'production_approved':False,
            'cross_border_catalogue_required_for_peak_metrics':True,'skyline_and_peak_benchmarks_complete':False}
    atomic_json(PROJECT/f'data/processed/pilot_{phase}.json',report)
    return report

