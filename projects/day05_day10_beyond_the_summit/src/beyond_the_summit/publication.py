"""G6: reproducible static explorer and publication reports, no deployment."""
from __future__ import annotations
import json,shutil,time
from pathlib import Path
import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
from rasterio.enums import Resampling
from rasterio.warp import reproject,calculate_default_transform
from affine import Affine
from pyproj import Transformer
from jinja2 import Environment,FileSystemLoader,select_autoescape
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LightSource
from matplotlib.ticker import MaxNLocator
import yaml
from .runtime import PROJECT,REPOSITORY,config,require_resources,fingerprint,atomic_json

PAPER='#f5f3eb';INK='#233f38';GREEN='#416e5c';GOLD='#bd9657'

def read_json(path):return json.loads(path.read_text(encoding='utf-8'))

def write_json(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,allow_nan=False,separators=(',',':')),encoding='utf-8')

def verify_manifest(path):
    m=read_json(path)
    for name,sha in m['files'].items():
        if fingerprint(PROJECT/name)!=sha:raise ValueError('Modified source: '+name)
    return m

def process_log_summary():
    starts=[];finishes=[];files=[]
    for file in sorted((PROJECT/'logs/runs').glob('*.jsonl')):
        files.append({'file':file.name,'sha256':fingerprint(file)})
        for line in file.read_text(encoding='utf-8').splitlines():
            if not line.strip():continue
            event=json.loads(line)
            if event.get('event')=='start':starts.append(event)
            if event.get('event')=='finish':finishes.append(event)
    return {'captured_execution_starts':len(starts),'captured_finishes':len(finishes),
        'successful_finishes':sum(e.get('status')=='success' for e in finishes),
        'failed_finishes':sum(e.get('status')=='failure' for e in finishes),
        'captured_prompt_files':len(list((PROJECT/'docs/prompts').glob('*'))),
        'first_recorded_start_utc':min((e['timestamp_utc'] for e in starts),default=None),
        'last_recorded_finish_utc':max((e['timestamp_utc'] for e in finishes),default=None),
        'coverage_note':'Captured CLI executions and supplied prompts, not complete agent iterations or active development hours. Concurrent/overlapping run durations must not be summed as elapsed work.',
        'run_files':files}

def terrain_backdrop(dem,web,assets):
    """Read a bounded preview, then warp the preview only; not analysis terrain."""
    with rasterio.open(dem) as ds:
        shape=(700,700);a=ds.read(1,out_shape=shape,resampling=Resampling.bilinear)
        transform=ds.transform*Affine.scale(ds.width/shape[1],ds.height/shape[0])
        valid=(a!=ds.nodata)&np.isfinite(a);filled=np.where(valid,a,0)
        shade=LightSource(azdeg=315,altdeg=45).hillshade(filled,dx=transform.a,dy=-transform.e)
        gray=np.where(valid,.40+.55*shade,1.)
        rgb=np.dstack([gray*.98,gray,gray*.95,np.where(valid,1.,0.)])
        bounds=ds.bounds;extent=[bounds.left,bounds.right,bounds.bottom,bounds.top]
        tr,w,h=calculate_default_transform(ds.crs,4326,shape[1],shape[0],*bounds)
        dst=np.zeros((h,w,4),dtype=np.float32)
        for channel in range(4):reproject(rgb[:,:,channel],dst[:,:,channel],src_transform=transform,src_crs=ds.crs,dst_transform=tr,dst_crs=4326,resampling=Resampling.bilinear)
    plt.imsave(web/'terrain.png',np.clip(dst,0,1))
    plt.imsave(assets/'terrain_native.png',np.clip(rgb,0,1))
    return {'bounds':[[tr.f+h*tr.e,tr.c],[tr.f,tr.c+w*tr.a]],'gray':gray,'extent':extent}

def build_site(scores,web,assets,terrain,provenance):
    cfg=config();targets=gpd.read_parquet(PROJECT/'data/processed/target_peaks.parquet')
    tx=Transformer.from_crs(32642,4326,always_xy=True)
    lon,lat=tx.transform(targets.geometry.x.to_numpy(),targets.geometry.y.to_numpy())
    target_list=[{'id':r.target_id,'name':str(r['name']) if pd.notna(r['name']) else r.target_id,'lat':round(float(lat[i]),6),'lon':round(float(lon[i]),6)} for i,(_,r) in enumerate(targets.iterrows())]
    target_index={r['id']:i for i,r in enumerate(target_list)}
    registry=pd.read_csv(PROJECT/'data/processed/mps/horizon_registry.csv')
    landmark_ids=set(registry.target_id);landmarks=registry[['target_id','name','official_ordinal']].to_dict('records')
    summits=[];details=web/'data/details';details.mkdir(parents=True,exist_ok=True)
    for i,r in scores.iterrows():
        if i%50==0:require_resources(cfg)
        marker=read_json(PROJECT/r.checkpoint)
        def artifact(suffix):
            name=next(k for k in marker['artifact_sha256'] if k.endswith(suffix));path=PROJECT/name
            if fingerprint(path)!=marker['artifact_sha256'][name]:raise ValueError('Modified G4 artifact: '+name)
            return path
        edges=pd.read_parquet(artifact('_edges.parquet'))
        visible=edges[edges.visible.fillna(False)]
        horizon=read_json(artifact('_horizon.json'))
        az=np.array(horizon['azimuth_true_degrees']);angle=np.array(horizon['horizon_degrees'])
        profile=[[round(float(a),2),round(float(b),3)] for a,b in zip(az[::10],angle[::10])]
        profile.sort(key=lambda pair:pair[0])
        view_path=artifact('_view.tif')
        with rasterio.open(view_path) as ds:
            preview=ds.read(1,out_shape=(800,800),resampling=Resampling.nearest)
            src_transform=ds.transform*Affine.scale(ds.width/800,ds.height/800)
            transform,width,height=calculate_default_transform(ds.crs,3857,800,800,*ds.bounds)
            warped=np.full((height,width),255,dtype=np.uint8)
            reproject(preview,warped,src_transform=src_transform,src_crs=ds.crs,
                dst_transform=transform,dst_crs=3857,src_nodata=255,dst_nodata=255,resampling=Resampling.nearest)
        from PIL import Image
        rgba=np.zeros((height,width,4),dtype=np.uint8);rgba[:,:,:3]=[0,145,220];rgba[:,:,3]=np.where(warped==1,170,0)
        overlay=web/'data/viewsheds'/(r.observer_id.replace(':','_')+'.png');overlay.parent.mkdir(exist_ok=True)
        Image.fromarray(rgba).save(overlay,optimize=True)
        to_geo=Transformer.from_crs(3857,4326,always_xy=True)
        west,south=to_geo.transform(transform.c,transform.f+height*transform.e)
        east,north=to_geo.transform(transform.c+width*transform.a,transform.f)
        write_json(details/(r.observer_id.replace(':','_')+'.json'),{'profile':profile,'display_step_degrees':1,
            'viewshed':{'url':overlay.relative_to(web).as_posix(),'bounds':[[south,west],[north,east]],'preview_only':True},
            'visible':[[target_index[e.target_id],round(float(e.distance_geodesic_m),1)] for e in visible.itertuples()],
            'unknown_target_ids':edges.loc[edges.visible.isna(),'target_id'].tolist()})
        x,y=tx.transform(r.x,r.y)
        summits.append({'id':r.observer_id,'name':r.display_name,'aliases':' '.join(str(r[c]) for c in ['name','name:ru','name:en'] if pd.notna(r[c])),
            'elevation':round(float(r.elevation_m),2),'lat':round(y,6),'lon':round(x,6),'band':r.elevation_band,
            'components':[float(r[c]) for c in ['terrain','peaks','skyline','distance']],
            'nps':float(r.nps),'mps':float(r.mps),'nps_rank':int(r.position),'mps_rank':int(r.mps_position),
            'landmark_score':float(r.landmark_score_lower),'visible_peaks':int(r.visible_peak_ground_proxies),
            'visible_area':float(r.visible_area_km2),'max_distance':float(r.maximum_visible_peak_distance_km),
            'skyline_contrast':float(r.skyline_prominence_sum_degrees),
            'horizon_visible':sorted(set(visible.target_id)&landmark_ids)})
    special=read_json(PROJECT/'data/processed/g5/special_winners.json')
    d={'summits':summits,'targets':target_list,'landmarks':landmarks,'landmark_targets':sorted(landmark_ids),
        'bounds':[[min(r['lat'] for r in summits),min(r['lon'] for r in summits)],[max(r['lat'] for r in summits),max(r['lon'] for r in summits)]],
        'terrain_bounds':terrain['bounds'],'specials':[{'label':k.replace('_',' '),'id':v['observer_id']} for k,v in special.items()]}
    write_json(web/'data/explorer.json',d)
    env=Environment(loader=FileSystemLoader(PROJECT/'templates'),autoescape=select_autoescape(['html']))
    import hashlib
    version=hashlib.sha256(''.join(fingerprint(PROJECT/'templates'/n) for n in ['app.js','style.css','i18n.js']).encode()).hexdigest()[:12]
    html=env.get_template('explorer.html').render(asset_version=version,weights=zip(['terrain','peaks','skyline','distance'],['Terrain','Visible peaks','Skyline','Distance'],[30,25,30,15]),
        bands=sorted(set(scores.elevation_band)),landmarks=landmarks)
    (web/'index.html').write_text(html,encoding='utf-8')
    for name in ['style.css','scores.js','i18n.js','app.js']:shutil.copy2(PROJECT/'templates'/name,web/name)
    vendor=PROJECT/'data/raw/publication/vendor'
    sources=read_json(vendor/'sources.json')
    for name,row in sources.items():
        if fingerprint(vendor/name)!=row['sha256']:raise ValueError('Vendor hash mismatch')
        target=web/'vendor'/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(vendor/name,target)
    downloads=web/'downloads';downloads.mkdir(exist_ok=True)
    shutil.copy2(PROJECT/'data/processed/mps/rankings.csv',downloads/'rankings.csv')
    method='\n\n'.join((PROJECT/'docs'/name).read_text(encoding='utf-8') for name in ['g5_methodology.md','mps_methodology.md','mps_scope_clarification.md'])
    (downloads/'methodology.md').write_text(method,encoding='utf-8')
    write_json(downloads/'provenance.json',provenance)
    return d

def plot_assets(scores,assets,terrain):
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.facecolor':PAPER,'figure.facecolor':PAPER,'text.color':INK,'axes.labelcolor':INK,'xtick.color':INK,'ytick.color':INK,'axes.edgecolor':'#cbd1c6'})
    paths={}
    def save(fig,name):
        path=assets/(name+'.png');fig.savefig(path,dpi=180,bbox_inches='tight',facecolor=PAPER);plt.close(fig);paths[name]=path
    fig,ax=plt.subplots(figsize=(10,7))
    ax.imshow(terrain['gray'],extent=terrain['extent'],cmap='gray',vmin=0,vmax=1,alpha=.65)
    scatter=ax.scatter(scores.x,scores.y,c=scores.nps,cmap='YlGn',s=9,vmin=0,vmax=100,linewidth=0)
    for label,col in [('NPS','position'),('MPS','mps_position')]:
        r=scores.loc[scores[col].idxmin()];ax.scatter([r.x],[r.y],marker='*',s=200,c=GOLD,edgecolors=INK,zorder=5)
        ax.annotate(label+' #1',(r.x,r.y),xytext=(12,12 if label=='NPS' else -18),textcoords='offset points',fontsize=11,color=INK,weight='bold')
    ax.set_xlim(scores.x.min()-14000,scores.x.max()+14000);ax.set_ylim(scores.y.min()-14000,scores.y.max()+14000)
    ax.set_aspect('equal');ax.set_xlabel('UTM easting · EPSG:32642');ax.set_ylabel('UTM northing');ax.ticklabel_format(style='plain',axis='both');ax.grid(alpha=.15)
    ax.xaxis.set_major_locator(MaxNLocator(4))
    fig.colorbar(scatter,ax=ax,shrink=.65,label='Published NPS / 100');save(fig,'ranking_map')
    example=scores.loc[scores.mps_position.idxmin()];marker=read_json(PROJECT/example.checkpoint)
    view=PROJECT/next(k for k in marker['artifact_sha256'] if k.endswith('_view.tif'))
    with rasterio.open(view) as ds:
        a=ds.read(1,out_shape=(600,600),resampling=Resampling.nearest);b=ds.bounds
    fig,ax=plt.subplots(figsize=(5,3.5));ax.imshow(terrain['gray'],extent=terrain['extent'],cmap='gray',alpha=.5)
    ax.imshow(np.ma.masked_where(a!=1,a),extent=[b.left,b.right,b.bottom,b.top],cmap='Greens',vmin=0,vmax=1,alpha=.55)
    ax.scatter([example.x],[example.y],c=GOLD,s=60,marker='*');ax.set_xlim(b.left,b.right);ax.set_ylim(b.bottom,b.top);ax.set_aspect('equal');ax.set_axis_off();save(fig,'viewshed')
    horizon=read_json(PROJECT/next(k for k in marker['artifact_sha256'] if k.endswith('_horizon.json')))
    fig,ax=plt.subplots(figsize=(5,3.5));az=np.array(horizon['azimuth_true_degrees']);order=np.argsort(az)
    ax.plot(az[order],np.array(horizon['horizon_degrees'])[order],color=GREEN,lw=1);ax.axhline(0,color=GOLD,lw=.8)
    ax.set_xlim(0,360);ax.set_xticks([0,90,180,270,360]);ax.set_xlabel('True bearing, degrees');ax.set_ylabel('Signed horizon angle, degrees');ax.grid(alpha=.18);save(fig,'skyline')
    edges=pd.read_parquet(PROJECT/next(k for k in marker['artifact_sha256'] if k.endswith('_edges.parquet')));edges=edges[edges.visible.fillna(False)]
    registry=pd.read_csv(PROJECT/'data/processed/mps/horizon_registry.csv');ids=set(registry.target_id)
    fig,ax=plt.subplots(figsize=(5,3.5))
    for e in edges.itertuples():ax.plot([example.x,e.target_x],[example.y,e.target_y],color=GOLD if e.target_id in ids else GREEN,alpha=.7 if e.target_id in ids else .10,lw=1 if e.target_id in ids else .5)
    ax.scatter(edges.target_x,edges.target_y,s=4,color=GREEN);ax.scatter([example.x],[example.y],s=80,marker='*',c=GOLD);ax.set_aspect('equal');ax.set_axis_off();save(fig,'network')
    fig,ax=plt.subplots(figsize=(6,4));ax.scatter(scores.elevation_m,scores.nps,s=10,c=GREEN,alpha=.45,edgecolor='none');ax.set_xlabel('Summit elevation, m');ax.set_ylabel('NPS / 100');ax.grid(alpha=.15);save(fig,'elevation')
    top=scores.sort_values('mps_position').head(10).iloc[::-1];fig,ax=plt.subplots(figsize=(6,4))
    labels=[(r.display_name if not r.display_name.startswith('node:') else r.observer_id.replace('node:','#')) for r in top.itertuples()]
    y=np.arange(10);ax.barh(y-.18,top.nps,height=.34,color=GREEN,label='NPS');ax.barh(y+.18,top.mps,height=.34,color=GOLD,label='MPS')
    ax.set_yticks(y,labels);ax.set_xlim(0,100);ax.set_xlabel('Score / 100 · top ten by MPS');ax.legend(frameon=False,loc='lower right');save(fig,'top10')
    return paths

def build_publication():
    started=time.monotonic();cfg=config();require_resources(cfg)
    verify_manifest(PROJECT/'data/processed/g5_manifest.json');verify_manifest(PROJECT/'data/processed/mps_manifest.json')
    publication=yaml.safe_load((PROJECT/'config/publication.yaml').read_text())
    web=PROJECT/'web';web.mkdir(exist_ok=True);assets=PROJECT/'report/g6/assets';assets.mkdir(parents=True,exist_ok=True)
    scores=pd.read_parquet(PROJECT/'data/processed/mps/rankings.parquet')
    status=read_json(PROJECT/'data/processed/g4_status.json');logs=process_log_summary()
    terrain=terrain_backdrop(PROJECT/'data/interim/pilot_dem_30m.tif',web,assets)
    provenance={'build':'G6 local export','publication':publication,'analysis':{'backend':'GDAL 3.12.3 GVM_Edge','radius_projected_m':100000,'dem_resolution_m':30,'observer_height_m':1.7,'refraction_coefficient':.14286,'observers':1302,'targets':2052,'horizon_landmarks':15,'osm_snapshot':'2026-11-02T21:21:26Z','g4_signature':status['signature']},
        'g5_manifest_sha256':fingerprint(PROJECT/'data/processed/g5_manifest.json'),'mps_manifest_sha256':fingerprint(PROJECT/'data/processed/mps_manifest.json'),
        'sources':{'OSM':'https://www.openstreetmap.org/copyright','Copernicus DEM':'https://dataspace.copernicus.eu/explore-data/data-collections/copernicus-contributing-missions/collections-description/COP-DEM','Horizon':'https://gorets.uz/21-gorizont/'}}
    build_site(scores,web,assets,terrain,provenance)
    plots=plot_assets(scores,assets,terrain)
    from .publication_pdf import reports
    pdfs=reports(scores,plots,logs,publication)
    for pdf in pdfs:shutil.copy2(pdf,web/'downloads'/pdf.name)
    write_json(PROJECT/'report/g6/process_log_summary.json',logs)
    (web/'.nojekyll').write_text('',encoding='utf-8')
    summary={'stage':'G6 local export','deployment':'not performed','wall_seconds':time.monotonic()-started,
        'generator_sha256':fingerprint(Path(__file__)),
        'pdf_generator_sha256':fingerprint(PROJECT/'src/beyond_the_summit/publication_pdf.py'),
        'templates':{f.name:fingerprint(f) for f in (PROJECT/'templates').iterdir() if f.is_file()},
        'site_files':len(list(web.rglob('*'))),'site_bytes':sum(f.stat().st_size for f in web.rglob('*') if f.is_file()),
        'reports':[str(p.relative_to(PROJECT)) for p in pdfs],
        'inputs':provenance,'files':{str(f.relative_to(PROJECT)):fingerprint(f)
            for directory in [web,PROJECT/'report/g6'] for f in directory.rglob('*')
            if f.is_file() and not any(part.startswith('qa') for part in f.relative_to(directory).parts)}}
    atomic_json(PROJECT/'data/processed/g6_export.json',summary)
    return {k:v for k,v in summary.items() if k not in ['files','inputs']}

def stage_pages():
    """Copy only G6 outputs to new docs/day05; never touch Days 01–04."""
    summary=read_json(PROJECT/'data/processed/g6_export.json')
    for name,sha in summary['files'].items():
        if fingerprint(PROJECT/name)!=sha:raise ValueError('Export changed: '+name)
    source=PROJECT/'web';dest=REPOSITORY/'docs/day05'
    if dest.exists() and not (dest/'bts-export.json').exists():
        existing=[p for p in dest.rglob('*') if p.is_file() and p.name!='.gitkeep']
        if existing:raise ValueError('Refuse to overwrite unowned Pages directory')
    shutil.copytree(source,dest,dirs_exist_ok=True)
    marker={'export_sha256':fingerprint(PROJECT/'data/processed/g6_export.json'),'files':{str(f.relative_to(source)):fingerprint(f) for f in source.rglob('*') if f.is_file()}}
    atomic_json(dest/'bts-export.json',marker)
    return {'directory':str(dest),'files':len(marker['files']),'published':False}
