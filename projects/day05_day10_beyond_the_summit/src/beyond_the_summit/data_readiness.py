"""G2: bounded terrain certification, OSM target acquisition and landmark QA."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
from html.parser import HTMLParser
import json
import math
from pathlib import Path
import re
import time
import xml.etree.ElementTree as ET

import geopandas as gpd
import numpy as np
import pandas as pd
from pyproj import Transformer
import rasterio
import requests
from scipy.spatial import cKDTree
from shapely.geometry import Point

from .runtime import PROJECT, REPOSITORY, Run, atomic_json, config, fingerprint, require_resources

DEM = PROJECT/'data/interim/pilot_dem_30m.tif'
PROCESSED = PROJECT/'data/processed'
RAW = PROJECT/'data/raw/g2'
PROGRAMS = {'Horizon':'21-gorizont', 'Mirage':'21-mirazh',
            'Cascade':'21-kaskad','Underground':'21-podzemele'}


def parse_roster(html, program):
    """Keep numbered official groups; do not turn grouped lakes into invented IDs."""
    class Text(HTMLParser):
        def __init__(self):super().__init__();self.parts=[];self.ignored=0
        def handle_starttag(self,tag,attrs):
            if tag in ('script','style'):self.ignored+=1
            if tag in ('p','div','li','h1','h2','h3','br'):self.parts.append('\n')
        def handle_endtag(self,tag):
            if tag in ('script','style'):self.ignored=max(0,self.ignored-1)
            if tag in ('p','div','li','h1','h2','h3'):self.parts.append('\n')
        def handle_data(self,data):
            if not self.ignored:self.parts.append(data)
    parser=Text();parser.feed(html)
    lines=[' '.join(s.split()) for s in ''.join(parser.parts).splitlines()]
    header={'Horizon':'21 вершина','Mirage':'21 озеро','Cascade':'21 водопад','Underground':'21 подземелье'}[program]
    started=False;entries=[]
    for line in lines:
        if header in line.lower():started=True;continue
        if not started:continue
        if 'ДОКАЗАТЕЛЬСТВА' in line.upper():break
        match=re.match(r'^(\d{1,2})\s*[.)]\s*(.+)',line)
        if match and 1<=int(match.group(1))<=21:
            ordinal=int(match.group(1));text=match.group(2)
            if not any(e['ordinal']==ordinal and e['text']==text for e in entries):
                entries.append({'program':program,'ordinal':ordinal,'text':text})
    return entries


def write_parquet(frame, path):
    path.parent.mkdir(parents=True,exist_ok=True)
    partial=path.with_suffix('.partial.parquet')
    frame.to_parquet(partial,index=False)
    partial.replace(path)


def parse_elevation(value):
    """Conservative OSM metre parser; keep ambiguous/raw values separately."""
    if value is None:return None
    text=str(value).strip().replace('\u00a0',' ')
    if re.fullmatch(r'[+-]?\d{1,3},\d{3}\s*(?:m|м)?',text,re.I):return None
    match=re.fullmatch(r'([+-]?\d+(?:[.,]\d+)?)\s*(?:m|м)?',text,re.I)
    if not match:return None
    height=float(match.group(1).replace(',','.'))
    return height if math.isfinite(height) and -500<=height<=9000 else None


def certify_coverage(dem, observers, cfg, run=None):
    """Check every invalid cell against nearest observer: exact circle union.

    No polygon approximation or per-observer full raster reread is required.
    A zero bad-cell count proves valid support for every observer's circle.
    """
    started=time.monotonic()
    xy=np.column_stack([observers.geometry.x,observers.geometry.y])
    tree=cKDTree(xy)
    bad_count=invalid_count=0
    examples=[]
    with rasterio.open(dem) as source:
        if source.crs is None or source.crs.to_string()!=cfg['analysis']['crs']:
            raise ValueError('Coverage DEM CRS differs from configured projected grid')
        t=source.transform
        if t.b or t.d or t.a<=0 or t.e>=0 or not np.isclose(t.a,-t.e):
            raise ValueError('Coverage requires north-up square cells')
        radius=cfg['analysis']['radius_m']+2*t.a
        b=source.bounds
        in_bounds=((xy[:,0]-radius>=b.left)&(xy[:,0]+radius<=b.right)&
                   (xy[:,1]-radius>=b.bottom)&(xy[:,1]+radius<=b.top))
        for index,(_,window) in enumerate(source.block_windows(1)):
            if index%50==0:
                require_resources(cfg)
                if run:run.event('coverage_progress',blocks_completed=index)
                if time.monotonic()-started>900:raise TimeoutError('Coverage audit exceeded 15 minutes')
            a=source.read(1,window=window,masked=True)
            invalid=np.ma.getmaskarray(a)|~np.isfinite(a.data)
            rr,cc=np.where(invalid)
            invalid_count+=len(rr)
            if not len(rr):continue
            points=np.column_stack([t.c+(window.col_off+cc+.5)*t.a,
                                    t.f+(window.row_off+rr+.5)*t.e])
            distances,nearest=tree.query(points,k=1,workers=1)
            bad=distances<=radius
            bad_count+=int(bad.sum())
            for j in np.flatnonzero(bad)[:max(0,10-len(examples))]:
                examples.append({'x':float(points[j,0]),'y':float(points[j,1]),
                                 'nearest_observer_id':str(observers.iloc[int(nearest[j])].observer_id),
                                 'distance_m':float(distances[j])})
        result={'passed':bool(in_bounds.all() and bad_count==0),'observer_count':len(observers),
                'radius_m':cfg['analysis']['radius_m'],'halo_m':2*t.a,
                'observers_with_full_bounds':int(in_bounds.sum()),
                'invalid_cells_entire_mosaic':invalid_count,'invalid_cells_within_circle_union_and_halo':bad_count,
                'invalid_examples':examples,'dem':str(Path(dem).relative_to(REPOSITORY)),
                'dem_sha256':fingerprint(dem),'observer_fingerprint':fingerprint(PROCESSED/'observers.parquet') if (PROCESSED/'observers.parquet').exists() else None,
                'wall_seconds':time.monotonic()-started,'method':'all raster cells; nearest-observer exact projected radius union',
                'crs':source.crs.to_string(),'resolution_m':source.res[0],
                'vertical_reference':'Copernicus GLO-30 EGM2008 lineage; local metadata not independently certified'}
    return result


def fetch_overpass(bounds, snapshot, cfg, run):
    """Small thematic extract instead of downloading entire country PBFs."""
    left,bottom,right,top=bounds
    query=(f'[out:json][timeout:120][maxsize:134217728][date:"{snapshot}"];'
           f'nwr["natural"="peak"]({bottom:.8f},{left:.8f},{top:.8f},{right:.8f});out meta center;')
    key=hashlib.sha256(query.encode()).hexdigest()[:16]
    path=RAW/f'peaks_{key}.json';meta=path.with_suffix('.source.json')
    RAW.mkdir(parents=True,exist_ok=True)
    if path.exists() and meta.exists():
        prior=json.loads(meta.read_text(encoding='utf-8'))
        if prior.get('query')==query and prior.get('sha256')==fingerprint(path):
            return json.loads(path.read_text(encoding='utf-8')),prior
        raise ValueError('Cached OSM response failed provenance validation')
    failures=[]
    for endpoint in ['https://overpass-api.de/api/interpreter','https://overpass.kumi.systems/api/interpreter']:
        partial=path.with_suffix('.partial.json')
        try:
            require_resources(cfg,additional_disk_bytes=16*2**20)
            started=time.monotonic()
            with requests.post(endpoint,data={'data':query},stream=True,timeout=(20,160),
                               headers={'User-Agent':'BeyondTheSummit/0.1 (30DayMapChallenge; bounded thematic extract)'}) as response:
                response.raise_for_status()
                size=0
                with partial.open('wb') as output:
                    for chunk in response.iter_content(65536):
                        require_resources(cfg)
                        size+=len(chunk)
                        if size>16*2**20:raise ValueError('OSM thematic response exceeds 16 MiB budget')
                        if time.monotonic()-started>240:raise TimeoutError('OSM request exceeds 4 minutes')
                        output.write(chunk)
            data=json.loads(partial.read_text(encoding='utf-8'))
            if data.get('remark') or not isinstance(data.get('elements'),list):
                raise ValueError(f'Incomplete/error Overpass result: {data.get("remark")}')
            record={'endpoint':endpoint,'query':query,'requested_snapshot_utc':snapshot,
                    'response_osm_base_utc':data.get('osm3s',{}).get('timestamp_osm_base'),
                    'retrieved_utc':datetime.now(timezone.utc).isoformat(),'bytes':size,
                    'sha256':fingerprint(partial),'license':'ODbL 1.0',
                    'attribution':'OpenStreetMap contributors','license_url':'https://www.openstreetmap.org/copyright',
                    'acquisition_method':'bounded Overpass nwr thematic query, snapshot aligned with existing PBF',
                    'failed_endpoints':failures}
            partial.replace(path);atomic_json(meta,record)
            run.event('osm_download',**record)
            return data,record
        except (requests.RequestException,ValueError,TimeoutError) as error:
            failures.append({'endpoint':endpoint,'error':str(error)})
            run.event('osm_download_failure',**failures[-1])
    raise RuntimeError('Cross-border OSM acquisition failed: '+json.dumps(failures))


def local_peaks(path,bounds,cfg):
    import osmium
    left,bottom,right,top=bounds
    key=hashlib.sha256(json.dumps({'pbf_sha256':fingerprint(path),'bounds':list(bounds)},sort_keys=True).encode()).hexdigest()
    cache=RAW/f'local_peaks_{key[:16]}.json';sidecar=cache.with_suffix('.sha256.json')
    if cache.exists() and sidecar.exists():
        if fingerprint(cache)!=json.loads(sidecar.read_text(encoding='utf-8'))['sha256']:
            raise ValueError('Local PBF peak cache integrity failed')
        data=json.loads(cache.read_text(encoding='utf-8'))
        return data['elements'],data['snapshot']
    reader=osmium.io.Reader(str(path),osmium.osm.NODE)
    header=reader.header()
    snapshot=header.get('osmosis_replication_timestamp')
    reader.close()
    if not snapshot:raise ValueError('Existing PBF has no verified snapshot timestamp')
    elements=[]
    processor=osmium.FileProcessor(str(path),osmium.osm.NODE).with_filter(osmium.filter.TagFilter(('natural','peak')))
    started=time.monotonic()
    for index,node in enumerate(processor):
        if index%500==0:
            require_resources(cfg)
            if time.monotonic()-started>300:raise TimeoutError('PBF peak extraction exceeded five minutes')
        if node.location.valid() and left<=node.location.lon<=right and bottom<=node.location.lat<=top:
            elements.append({'type':'node','id':int(node.id),'lon':node.location.lon,
                'lat':node.location.lat,'tags':dict(node.tags),'version':int(node.version),
                'timestamp':str(node.timestamp)})
    atomic_json(cache,{'elements':elements,'snapshot':snapshot,'source_key':key})
    atomic_json(sidecar,{'sha256':fingerprint(cache)})
    return elements,snapshot


def build_targets(observers,cfg,run):
    left,bottom,right,top=observers.total_bounds
    pad=cfg['analysis']['radius_m']+120
    # Conservative transformed enclosing rectangle, not a polygonized circle:
    # avoids missing target nodes between coarse buffer vertices.
    bounds=Transformer.from_crs(observers.crs,4326,always_xy=True).transform_bounds(
        left-pad,bottom-pad,right+pad,top+pad,densify_pts=64)
    path=REPOSITORY/cfg['study']['osm_file']
    local,snapshot=local_peaks(path,bounds,cfg)
    print(f'G2 local OSM: {len(local)} peaks; snapshot {snapshot}',flush=True)
    data,provenance=fetch_overpass(bounds,snapshot,cfg,run)
    remote=data['elements']
    if any(e.get('timestamp','')>snapshot for e in remote):
        raise ValueError('Overpass returned objects newer than the requested historical snapshot')
    # Do not merge out-of-snapshot geometries or silently replace missing remote nodes.
    records=[];non_nodes=[]
    for e in remote:
        if e['type']!='node':
            non_nodes.append(e);continue
        if e.get('tags',{}).get('natural')!='peak':raise ValueError('Unexpected non-peak OSM target')
        tags=e.get('tags',{})
        records.append({'target_id':f"node:{e['id']}",'osm_type':'node','osm_id':int(e['id']),
            'name':tags.get('name'),'name_ru':tags.get('name:ru'),'name_en':tags.get('name:en'),
            'ele_raw':tags.get('ele'),'ele_osm_m':parse_elevation(tags.get('ele')),
            'osm_version':e.get('version'),'osm_timestamp':e.get('timestamp'),
            'tags_json':json.dumps(tags,ensure_ascii=False,sort_keys=True),
            'geometry':Point(float(e['lon']),float(e['lat']))})
    if not records:raise ValueError('Cross-border peak query returned no point peaks')
    points=gpd.GeoDataFrame(records,crs=4326).to_crs(cfg['analysis']['crs'])
    if points.target_id.duplicated().any() or (~points.is_valid).any():raise ValueError('Invalid/duplicate target IDs')
    local_ids={f"node:{e['id']}" for e in local}
    remote_ids=set(points.target_id)
    missing_local=sorted(local_ids-remote_ids)
    if missing_local:raise ValueError(f'{len(missing_local)} local same-snapshot peaks absent from international query')
    remote_by_id={e['id']:e for e in remote if e['type']=='node'}
    geometry_mismatches=[e['id'] for e in local if
        abs(e['lon']-remote_by_id[e['id']]['lon'])>1e-7 or abs(e['lat']-remote_by_id[e['id']]['lat'])>1e-7]
    if geometry_mismatches:raise ValueError('Historical OSM point coordinates disagree with local PBF')
    observer_xy=np.column_stack([observers.geometry.x,observers.geometry.y])
    distances,_=cKDTree(observer_xy).query(np.column_stack([points.geometry.x,points.geometry.y]),workers=1)
    points['nearest_observer_distance_m']=distances
    points=points[distances<=cfg['analysis']['radius_m']].copy().reset_index(drop=True)
    with rasterio.open(DEM) as dem:
        ground=np.ma.concatenate(list(dem.sample([(p.x,p.y) for p in points.geometry],masked=True)))
        valid=~np.ma.getmaskarray(ground)&np.isfinite(ground.data)
        points['ground_dem_m']=np.where(valid,ground.data,np.nan)
    points['elevation_m']=points.ele_osm_m.fillna(points.ground_dem_m)
    points['elevation_source']=np.where(points.ele_osm_m.notna(),'OSM ele','DEM cell fallback')
    points['terrain_valid']=valid
    points['eligible_1800m']=points.elevation_m.ge(cfg['study']['minimum_elevation_m'])&points.terrain_valid
    points['same_xy_group']=points.geometry.apply(lambda g:f'{g.x:.6f},{g.y:.6f}')
    points['duplicate_location']=points.same_xy_group.duplicated(keep=False)
    # Exact coordinate duplicates are one physical target for counts; retain all IDs in QA table.
    points=points.sort_values(['eligible_1800m','target_id'],ascending=[False,True]).reset_index(drop=True)
    points['count_representative']=~points.same_xy_group.duplicated()
    points['snapshot_utc']=snapshot
    points['target_height_definition']='DEM cell ground; OSM elevation is for selection/display only'
    write_parquet(points,PROCESSED/'target_peaks_all.parquet')
    eligible=points[points.eligible_1800m&points.count_representative].copy()
    write_parquet(eligible,PROCESSED/'target_peaks.parquet')
    atomic_json(PROCESSED/'nonpoint_peaks_review.json',{'elements':non_nodes,
        'disposition':'excluded from point-summit catalogue; original OSM objects preserved for QA',
        'policy':'natural=peak is mapped as a node. Do not invent summit coordinates from way/relation centres.',
        'mapping_reference':'https://wiki.openstreetmap.org/wiki/Tag:natural%3Dpeak'})
    observed=set(observers.observer_id)
    summary={'passed':bool(valid.all() and observed.issubset(set(eligible.target_id))),'snapshot_utc':snapshot,
        'query_bounds_wgs84':list(bounds),'query_domain':'conservative enclosing projected rectangle with 120 m margin; exact radius-filtered afterwards',
        'source':provenance,'existing_pbf_sha256':fingerprint(path),
        'local_bbox_nodes':len(local),'remote_bbox_point_peaks':len(records),'nonpoint_peaks_excluded':len(non_nodes),
        'local_point_geometry_mismatches':len(geometry_mismatches),
        'peaks_within_100km_any_observer':len(points),'eligible_1800m_unique_locations':len(eligible),
        'eligible_from_outside_existing_pbf':int((~eligible.target_id.isin(local_ids)).sum()),
        'missing_dem_ground':int((~points.terrain_valid).sum()),'missing_or_unparsed_osm_ele':int(points.ele_osm_m.isna().sum()),
        'duplicate_coordinate_records':int(points.duplicate_location.sum()),
        'observer_ids_absent_from_target_catalogue':sorted(observed-set(eligible.target_id)),
        'below_1800m_count':int((~points.elevation_m.ge(1800)).sum()),
        'outputs':{'all':'data/processed/target_peaks_all.parquet','eligible':'data/processed/target_peaks.parquet'},
        'output_sha256':{name:fingerprint(PROCESSED/name) for name in ['target_peaks_all.parquet','target_peaks.parquet','nonpoint_peaks_review.json']},
        'dem_sha256':fingerprint(DEM),'observer_sha256':fingerprint(PROCESSED/'observers.parquet'),
        'limitations':'Point-summit catalogue complete relative to bounded OSM historical query, not all real summits; no approximate near-coordinate merging. Nonpoint objects excluded with QA evidence, not assigned artificial summit locations.'}
    atomic_json(PROCESSED/'target_catalogue.json',summary)
    return summary


def audit_landmarks(observers,cfg,run):
    source=REPOSITORY/cfg['study']['landmark_file']
    points=gpd.read_file(source,layer=cfg['study']['landmark_layer']).to_crs(cfg['analysis']['crs'])
    source_counts=points.program.value_counts().to_dict()
    points['program_source']=points.program
    points['program']=points.program.replace({'21 Горизонт':'Horizon','21 Мираж':'Mirage'})
    points['source_row']=np.arange(len(points))
    # Coordinate-based identity deduplicates memberships without inventing OSM identities.
    points['landmark_id']=points.geometry.apply(lambda g:'landmark:'+hashlib.sha256(f'{g.x:.3f},{g.y:.3f}'.encode()).hexdigest()[:16])
    xy=np.column_stack([points.geometry.x,points.geometry.y])
    nearest,_=cKDTree(np.column_stack([observers.geometry.x,observers.geometry.y])).query(xy,workers=1)
    points['nearest_observer_distance_m']=nearest
    points['within_analysis_scope']=nearest<=cfg['analysis']['radius_m']
    with rasterio.open(DEM) as dem:
        ground=np.ma.concatenate(list(dem.sample(xy,masked=True)))
        points['ground_dem_m']=np.where(~np.ma.getmaskarray(ground)&np.isfinite(ground.data),ground.data,np.nan)
    # Raw GPX provenance and exact coordinate matching, not fuzzy name inference.
    waypoint_lookup={};gpx_sources=[]
    for path in sorted((source.parents[1]/'raw').glob('*.gpx')):
        root=ET.parse(path).getroot()
        for w in root.findall('{*}wpt'):
            key=(round(float(w.attrib['lon']),7),round(float(w.attrib['lat']),7))
            waypoint_lookup.setdefault(key,[]).append({'file':str(path.relative_to(REPOSITORY)),
                'name':w.findtext('{*}name'),'type':w.findtext('{*}type'),
                'extensions':{e.tag.split('}')[-1]:e.text for e in w.findall('{*}extensions/*')}})
        gpx_sources.append({'file':str(path.relative_to(REPOSITORY)),'sha256':fingerprint(path)})
    wgs=points.to_crs(4326)
    details=[]
    for row,geo in zip(points.itertuples(),wgs.geometry):
        key=(round(geo.x,7),round(geo.y,7))
        details.append(waypoint_lookup.get(key,[]))
    points['gpx_exact_match']=list(map(bool,details))
    points['gpx_evidence_json']=[json.dumps(d,ensure_ascii=False) for d in details]
    points['object_type']=points.program.map({'Horizon':'summit','Mirage':'lake'}).fillna('unverified')
    points['excluded_from_ranking']=points.object_type.isin(cfg.get('landmarks',{}).get('excluded_object_types',[]))
    points['ranking_exclusion_reason']=np.where(points.excluded_from_ranking,'user-excluded object type','')
    points['coordinate_status']=np.where(points.gpx_exact_match,'reconciled to supplied GPX; not survey-verified','unreconciled')
    points['membership_status']='supplied GPX membership; official roster match pending'
    points['scoring_eligible']=False
    points['visibility_status']='not evaluated'
    write_parquet(points,PROCESSED/'landmarks_audited.parquet')
    # Keep link table for future deduplicated multi-program membership.
    write_parquet(pd.DataFrame(points[['landmark_id','program','source_row']]).drop_duplicates(),PROCESSED/'landmark_memberships.parquet')
    evidence=[];rosters=[]
    RAW.mkdir(parents=True,exist_ok=True)
    for program,slug in PROGRAMS.items():
        url=f'https://gorets.uz/{slug}/';path=RAW/f'{slug}.html'
        try:
            require_resources(cfg)
            if not path.exists():
                with requests.get(url,timeout=(15,45),stream=True) as response:
                    response.raise_for_status()
                    content=bytearray()
                    for chunk in response.iter_content(65536):
                        require_resources(cfg)
                        content.extend(chunk)
                        if len(content)>2*2**20:raise ValueError('Official roster response exceeds budget')
                    path.write_bytes(content)
                atomic_json(path.with_suffix('.source.json'),{'url':url,'retrieved_utc':datetime.now(timezone.utc).isoformat(),
                    'sha256':fingerprint(path),'use':'private source evidence; not republished raw'})
            record=json.loads(path.with_suffix('.source.json').read_text(encoding='utf-8'))
            if record['url']!=url or record['sha256']!=fingerprint(path):raise ValueError('Official roster cache integrity failed')
            entries=parse_roster(path.read_text(encoding='utf-8'),program)
            rosters.extend([{**e,'source_url':url,'source_sha256':record['sha256'],
                             'coordinate_status':'not resolved from official roster; no inferred coordinates'} for e in entries])
            evidence.append({'program':program,'url':url,'sha256':fingerprint(path),'acquired':True,
                'numbered_groups':len({e['ordinal'] for e in entries}),'numbered_text_records':len(entries)})
        except (requests.RequestException,ValueError) as error:
            evidence.append({'program':program,'url':url,'acquired':False,'error':str(error)})
    atomic_json(PROCESSED/'official_landmark_rosters.json',{'entries':rosters,
        'meaning':'Official numbered program groups; one group may contain multiple lakes/caves. No coordinates inferred.'})
    summary={'passed':False,'partial_registry_prepared':True,'source_sha256':fingerprint(source),
        'records':len(points),'unique_coordinate_objects':points.landmark_id.nunique(),
        'program_counts':points.program.value_counts().to_dict(),'source_program_counts':source_counts,
        'object_type_counts':points.object_type.value_counts().to_dict(),'gpx_reconciled':int(points.gpx_exact_match.sum()),
        'within_100km':int(points.within_analysis_scope.sum()),
        'in_scope_missing_dem_ground':int((points.within_analysis_scope&points.ground_dem_m.isna()).sum()),
        'gpx_sources':gpx_sources,'official_program_sources':evidence,
        'scoring_eligible_records':0,'missing_program_coordinates':['Cascade','Underground','Snow Leopard'],
        'excluded_from_ranking_records':int(points.excluded_from_ranking.sum()),
        'ranking_candidate_records':int((~points.excluded_from_ranking).sum()),
        'ranking_candidates_within_100km':int((~points.excluded_from_ranking&points.within_analysis_scope).sum()),
        'excluded_object_types':cfg.get('landmarks',{}).get('excluded_object_types',[]),
        'blockers':['Official roster-to-coordinate reconciliation incomplete; program labels count groups, not necessarily individual physical objects.',
                    'Cave interiors are not distant visual targets; waterfall/entrance eligibility requires object-specific review.'],
        'nps_blocked':False,'mps_ready':False}
    atomic_json(PROCESSED/'landmark_audit.json',summary)
    return summary


def run_readiness(run:Run,stage='all',entry_available_ram_gib=2):
    cfg=config()
    if not math.isfinite(entry_available_ram_gib) or entry_available_ram_gib<cfg['resources']['runtime_reserve_available_gib']:
        raise ValueError('G2 entry threshold cannot be below runtime reserve')
    cfg['resources']['pilot_entry_available_gib']=entry_available_ram_gib
    entry=require_resources(cfg,pilot=True)
    dem_manifest=json.loads(DEM.with_suffix('.manifest.json').read_text(encoding='utf-8'))
    if fingerprint(DEM)!=dem_manifest['sha256']:
        raise ValueError('Terrain mosaic differs from its source-lineage manifest')
    observers=gpd.read_parquet(PROCESSED/'observers.parquet')
    if len(observers)!=cfg['study']['expected_observers'] or observers.observer_id.duplicated().any():
        raise ValueError('Observer cohort differs from approved count/identities')
    stages=('coverage','targets','landmarks') if stage=='all' else (stage,)
    if any(s not in ('coverage','targets','landmarks') for s in stages):raise ValueError('Unknown G2 stage')
    for name in stages:
        print(f'G2 {name}: starting',flush=True)
        if name=='coverage':
            result=certify_coverage(DEM,observers,cfg,run)
            atomic_json(PROCESSED/'terrain_coverage.json',result)
            if not result['passed']:raise RuntimeError('Full-cohort terrain coverage failed; see terrain_coverage.json')
        elif name=='targets':result=build_targets(observers,cfg,run)
        else:result=audit_landmarks(observers,cfg,run)
        run.event('g2_stage_complete',name=name,passed=result['passed'])
        print(f'G2 {name}: completed (passed={result["passed"]})',flush=True)
    components={}
    for name,file in [('terrain','terrain_coverage.json'),('targets','target_catalogue.json'),('landmarks','landmark_audit.json')]:
        path=PROCESSED/file
        components[name]=json.loads(path.read_text(encoding='utf-8')) if path.exists() else {'passed':False,'status':'not run'}
    summary={'run_id':run.id,'entry_available_ram_gib':entry_available_ram_gib,'entry_resources':entry,
             'terrain_ready':components['terrain']['passed'],'target_catalogue_ready':components['targets']['passed'],
             'nps_data_ready':components['terrain']['passed'] and components['targets']['passed'],
             'mps_data_ready':components['landmarks']['passed'],
             'components':{k:{'passed':v['passed']} for k,v in components.items()},
             'production_approved':False,'scope':'G2 preparation only; no rankings or full-cohort viewsheds'}
    outputs=['terrain_coverage.json','target_catalogue.json','target_peaks_all.parquet','target_peaks.parquet',
             'nonpoint_peaks_review.json','landmark_audit.json','landmarks_audited.parquet',
             'landmark_memberships.parquet','official_landmark_rosters.json']
    summary['artifact_sha256']={f'data/processed/{name}':fingerprint(PROCESSED/name) for name in outputs if (PROCESSED/name).exists()}
    summary['source_sha256']={'data/interim/pilot_dem_30m.tif':fingerprint(DEM),
                             'data/processed/observers.parquet':fingerprint(PROCESSED/'observers.parquet')}
    summary['algorithm_sha256']=fingerprint(Path(__file__))
    summary['config_sha256']=fingerprint(PROJECT/'config/analysis.yaml')
    summary['environment_sha256']=fingerprint(PROJECT/'environment-win-64.lock.txt')
    atomic_json(PROCESSED/'g2_readiness.json',summary)
    return summary
