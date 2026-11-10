"""G5: integrity-checked exploratory NPS, robustness and descriptive statistics."""
from __future__ import annotations

import json
from pathlib import Path
import time

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
from scipy.ndimage import uniform_filter1d
from scipy.signal import find_peaks,peak_prominences
from scipy.stats import rankdata,spearmanr,pearsonr
import yaml

from .data_readiness import write_parquet
from .runtime import PROJECT,Run,atomic_json,config,fingerprint,require_resources

COMPONENTS=['terrain','peaks','skyline','distance']


def percentile_score(values):
    """Mid-distribution empirical percentile; real zero=0, missing stays missing.

    Positive constants score 50, zero constants 0. No cohort mean imputation.
    """
    a=np.asarray(values,dtype=float)
    if np.any(a[np.isfinite(a)]<0):raise ValueError('Ranking evidence cannot be negative')
    result=np.full(a.shape,np.nan);valid=np.isfinite(a)
    if valid.any():result[valid]=100*(rankdata(a[valid],method='average')-.5)/valid.sum()
    result[valid&(a==0)]=0
    return result


def component_scores(frame,ranking_cfg):
    out=frame.copy()
    for name in ['visible_area_km2','visible_peak_ground_proxies','skyline_prominence_sum_degrees',
                 'skyline_complexity','terrain_distance_proxy_km','peak_angular_relief_degrees']:
        out['normalized_'+name]=percentile_score(out[name])
    t,p,s,d=[ranking_cfg[name] for name in COMPONENTS]
    out['terrain']=t['area_percentile']*out.normalized_visible_area_km2+t['open_directions_fraction']*out.open_directions_fraction*100
    out['peaks']=p['visible_count_percentile']*out.normalized_visible_peak_ground_proxies+p['bearing_coverage_fraction']*out.peak_bearing_coverage_fraction*100
    out['skyline']=s['summed_angular_prominence_percentile']*out.normalized_skyline_prominence_sum_degrees+s['smoothed_complexity_percentile']*out.normalized_skyline_complexity
    out['distance']=d['band_weighted_terrain_distance_percentile']*out.normalized_terrain_distance_proxy_km+d['mean_positive_peak_angular_relief_percentile']*out.normalized_peak_angular_relief_degrees
    return out


def weighted_score(frame,weights):
    vector=np.array([weights[name] for name in COMPONENTS],dtype=float)
    if not np.isfinite(vector).all() or (vector<0).any() or not np.isclose(vector.sum(),1):
        raise ValueError('Weights must be finite, nonnegative and sum to one')
    # Matrix multiplication propagates missing inputs rather than renormalizing.
    return frame[COMPONENTS].to_numpy(dtype=float)@vector


def stable_order(ids,scores):
    return np.lexsort((np.asarray(ids,dtype=str),-np.asarray(scores,dtype=float)))


def skyline_metrics(horizon,cfg):
    angle=np.asarray(horizon['horizon_degrees'],dtype=float)
    distance=np.asarray(horizon['limiting_distance_projected_m'],dtype=float)
    step=float(horizon['angular_step_degrees'])
    if len(angle)!=3600 or not np.isfinite(angle).all() or not np.isfinite(distance).all():
        raise ValueError('Missing/nonfinite or unexpected skyline profile')
    if np.any(distance<15) or np.any(distance>100000):raise ValueError('Skyline limiting range outside model support')
    r=cfg['skyline'];n=len(angle);values=[]
    far=distance>=cfg['sensitivity']['nearfield_ablation_m']
    for scale in r['smoothing_degrees']:
        smooth=uniform_filter1d(angle,size=max(1,round(scale/step)),mode='wrap')
        periodic=np.tile(smooth,3)
        peaks=find_peaks(periodic)[0]
        peaks=peaks[(peaks>=n)&(peaks<2*n)]
        if len(peaks):
            prominence=peak_prominences(periodic,peaks,wlen=2*round(r['prominence_window_half_degrees']/step)+1)[0]
            keep=prominence>=r['minimum_angular_prominence_degrees']
            strength=float(prominence[keep].sum())
            far_strength=float(prominence[keep&far[peaks-n]].sum())
            count=int(keep.sum())
        else:strength=far_strength=0.;count=0
        slope=np.abs(smooth-np.roll(smooth,1))/step
        values.append({'scale':scale,'strength':strength,'count':count,'complexity':float(slope.mean()),
            'far_strength':far_strength,'far_complexity':float((slope*(far&np.roll(far,1))).mean())})
    return {'skyline_prominence_sum_degrees':float(np.mean([v['strength'] for v in values])),
        'skyline_complexity':float(np.mean([v['complexity'] for v in values])),
        'skyline_feature_count_mean':float(np.mean([v['count'] for v in values])),
        'nearfield_horizon_fraction':float((~far).mean()),
        'skyline_far_strength':float(np.mean([v['far_strength'] for v in values])),
        'skyline_far_complexity':float(np.mean([v['far_complexity'] for v in values])),
        'skyline_scale_05_strength':values[0]['strength'],'skyline_scale_05_complexity':values[0]['complexity'],
        'skyline_scale_20_strength':values[-1]['strength'],'skyline_scale_20_complexity':values[-1]['complexity']}


def extract_and_audit(run,rcfg):
    started=time.monotonic();cfg=config()
    status_path=PROJECT/'data/processed/g4_status.json'
    status=json.loads(status_path.read_text(encoding='utf-8'))
    if status['state']!='complete' or status['completed']!=1302 or status['failed']:
        raise RuntimeError('Complete successful G4 required before G5')
    spec=status['model_specification']
    if cfg['analysis']!=spec['analysis'] or cfg['landmarks']!=spec['landmarks']:
        raise ValueError('Physical model changed after G4')
    for name,digest in spec['inputs'].items():
        if fingerprint(PROJECT/name)!=digest:raise ValueError(f'G4 input fingerprint mismatch: {name}')
    for name,digest in spec['algorithms'].items():
        if fingerprint(Path(__file__).with_name(name))!=digest:raise ValueError(f'G4 algorithm fingerprint mismatch: {name}')
    if fingerprint(PROJECT/'environment-win-64.lock.txt')!=spec['environment']:raise ValueError('Environment lock mismatch')
    observers=gpd.read_parquet(PROJECT/'data/processed/observers.parquet')
    expected=set(observers.observer_id)
    if set(status['completed_checkpoints'])!=expected:raise ValueError('G4 completed observer set differs from approved cohort')
    aggregate=pd.read_parquet(PROJECT/'data/processed/g4_observer_metrics.parquet').set_index('observer_id')
    if len(aggregate)!=1302 or set(aggregate.index)!=expected or not aggregate.index.is_unique:
        raise ValueError('G4 aggregate has missing/duplicate observer IDs')
    target_ids=set(gpd.read_parquet(PROJECT/'data/processed/target_peaks.parquet').target_id)
    rows=[];files=bytes_checked=unknown=affected=los_count=ng_count=ng_agreed=0
    near_grazing_count=near_grazing_agreed=0;start_times=[];finish_times=[]
    for index,(oid,marker) in enumerate(sorted(status['completed_checkpoints'].items())):
        if index%25==0:
            require_resources(cfg);print(f'G5 audit: {index}/1302',flush=True)
            run.event('g5_audit_progress',completed=index)
        c=json.loads((PROJECT/marker).read_text(encoding='utf-8'))
        if c['status']!='complete' or c['signature']!=status['signature'] or c['observer']['observer_id']!=oid:
            raise ValueError('Invalid G4 completion marker')
        artifacts=c['artifact_sha256']
        if len(artifacts)!=5:raise ValueError('Unexpected G4 artifact set')
        for name,digest in artifacts.items():
            path=PROJECT/name
            if not path.is_relative_to(PROJECT) or fingerprint(path)!=digest:
                raise ValueError(f'G4 artifact missing or corrupt: {name}')
            files+=1;bytes_checked+=path.stat().st_size
        def product(suffix):return PROJECT/next(name for name in artifacts if name.endswith(suffix))
        terrain=c['terrain'];peaks=c['peaks']
        if not np.isclose(terrain['visible_area_km2'],terrain['visible_cells']*.0009):raise ValueError('Terrain area/cell mismatch')
        bands=terrain['distance_bands']
        if sum(b['visible_cells'] for b in bands)!=terrain['visible_cells'] or sum(b['cells'] for b in bands)!=terrain['circle_cells']:
            raise ValueError('Distance-band denominators do not reconcile')
        if any(b['visible_cells']<0 or b['visible_cells']>b['cells'] for b in bands):raise ValueError('Invalid band visibility counts')
        with rasterio.open(product('_view.tif')) as view:
            if view.crs.to_epsg()!=32642 or view.res!=(30.,30.) or view.nodata!=255 or view.dtypes!=('uint8',):
                raise ValueError('Unexpected raster grid/type/NoData')
        edges=pd.read_parquet(product('_edges.parquet'))
        if len(edges)!=peaks['eligible_targets_in_radius'] or not edges.target_id.is_unique or oid in set(edges.target_id):
            raise ValueError('Peak edge denominator, duplicates or self-edge error')
        if not set(edges.target_id).issubset(target_ids) or not edges.observer_id.eq(oid).all():raise ValueError('Unrecognized edge identity')
        if (edges.distance_projected_m>100000).any() or (edges.distance_projected_m<=0).any():raise ValueError('Invalid target range')
        visible=edges[edges.visible.fillna(False)]
        if len(visible)!=peaks['visible_peak_ground_proxies'] or int(edges.visible.isna().sum())!=peaks['unknown_targets']:
            raise ValueError('Peak visibility summary differs from sparse edges')
        unknown+=peaks['unknown_targets'];affected+=int(peaks['unknown_targets']>0)
        if c['landmarks']['lake_records_sampled']!=0:raise ValueError('Excluded lake entered analysis')
        horizon=json.loads(product('_horizon.json').read_text(encoding='utf-8'))
        los=json.loads(product('_los.json').read_text(encoding='utf-8'))
        checks=los['checks'];nongrazing=[x for x in checks if not x['near_grazing_2m']]
        if len(checks)!=los['count'] or len(nongrazing)!=los['non_grazing_count']:raise ValueError('LOS diagnostic counts inconsistent')
        los_count+=len(checks);ng_count+=len(nongrazing);ng_agreed+=sum(x['agrees'] for x in nongrazing)
        grazing=[x for x in checks if x['near_grazing_2m']]
        near_grazing_count+=len(grazing);near_grazing_agreed+=sum(x['agrees'] for x in grazing)
        areas=np.array([b['visible_area_km2'] for b in bands])
        dproxy=float(np.dot(areas,rcfg['distance']['terrain_band_midpoints_km'])/areas.sum()) if areas.sum()>0 else 0.
        if len(visible):
            d=visible.distance_projected_m.to_numpy()
            relief=visible.target_ground_dem_m.to_numpy()-horizon['effective_ground_dem_m']-cfg['analysis']['observer_height_m']
            relief-=(1-cfg['analysis']['refraction_coefficient'])*d*d/(2*6378137.)
            apparent=float(np.maximum(np.rad2deg(np.arctan2(relief,d)),0).mean())
        else:apparent=0.
        raw={'observer_id':oid,'elevation_m':c['observer']['elevation_m'],'x':c['observer']['x'],'y':c['observer']['y'],
            'ground_dem_m':horizon['effective_ground_dem_m'],'visible_area_km2':terrain['visible_area_km2'],
            'visible_peak_ground_proxies':len(visible),'eligible_peak_targets':len(edges),
            'unknown_peak_targets':peaks['unknown_targets'],'peak_bearing_coverage_fraction':peaks['ten_degree_true_bearing_sectors_occupied']/36,
            'open_directions_fraction':terrain['ten_degree_sectors_with_visible_ground_beyond_20km']/36,
            'terrain_distance_proxy_km':dproxy,'peak_angular_relief_degrees':apparent,
            'maximum_visible_peak_distance_km':float(visible.distance_geodesic_m.max()/1000) if len(visible) else 0.,
            'non_grazing_los_agreement':sum(x['agrees'] for x in nongrazing)/len(nongrazing) if nongrazing else np.nan,
            'checkpoint':marker,**skyline_metrics(horizon,rcfg)}
        if not np.isclose(raw['visible_area_km2'],aggregate.loc[oid,'visible_area_km2']) or raw['visible_peak_ground_proxies']!=aggregate.loc[oid,'visible_peak_ground_proxies']:
            raise ValueError('G4 aggregate differs from verified observer marker')
        rows.append(raw)
    audit={'passed':True,'observers':len(rows),'verified_artifact_files':files,'verified_bytes':bytes_checked,
        'unknown_peak_observations':unknown,'observers_with_unknown_targets':affected,
        'los_count':los_count,'non_grazing_los_count':ng_count,'non_grazing_los_agreed':ng_agreed,
        'non_grazing_agreement':ng_agreed/ng_count if ng_count else None,
        'near_grazing_count':near_grazing_count,'near_grazing_agreement':near_grazing_agreed/near_grazing_count if near_grazing_count else None,
        'wall_seconds':time.monotonic()-started,'g4_signature':status['signature'],
        'note':'Whole-product hashes and schema/cross-table checks; no expensive full raster visibility recomputation. Same-DSM LOS diagnostics are not ground truth.'}
    frame=pd.DataFrame(rows)
    names=observers.drop(columns='geometry').rename(columns={'ground_dem_m':'staged_ground_dem_m','elevation_m':'staged_elevation_m'})
    frame=frame.merge(names[['observer_id','name','name:ru','name:en','ridge_name','elevation_source']],on='observer_id',validate='one_to_one')
    frame['display_name']=frame['name'].fillna(frame['name:ru']).fillna(frame['name:en']).fillna(frame.observer_id)
    return frame,audit


def sensitivity(frame,weights,rcfg):
    base=np.asarray([weights[n] for n in COMPONENTS]);ids=frame.observer_id.to_numpy()
    baseline=stable_order(ids,frame.nps);base_top=set(ids[baseline[:10]])
    scenarios={'baseline':base,'equal_weights':np.ones(4)/4}
    for i,name in enumerate(COMPONENTS):
        w=np.full(4,.2);w[i]=.4;scenarios[name+'_priority']=w
        for factor,label in [(.8,'minus20pct'),(1.2,'plus20pct')]:
            w=base.copy();w[i]*=factor;w/=w.sum();scenarios[name+'_'+label]=w
    columns={};summary=[]
    def add(name,scores,vector=None):
        order=stable_order(ids,scores);positions=np.empty(len(ids),int);positions[order]=np.arange(1,len(ids)+1)
        columns[name]=positions
        summary.append({'scenario':name,'weights':dict(zip(COMPONENTS,vector.tolist())) if vector is not None else None,
            'winner':str(ids[order[0]]),'top10_overlap':len(base_top&set(ids[order[:10]])),
            'spearman_with_baseline':float(spearmanr(frame.nps,scores).statistic)})
    for name,w in scenarios.items():add(name,frame[COMPONENTS].to_numpy()@w,w)
    for label,strength,complexity in [('skyline_05_degree','skyline_scale_05_strength','skyline_scale_05_complexity'),
        ('skyline_20_degree','skyline_scale_20_strength','skyline_scale_20_complexity'),
        ('skyline_excluding_nearfield','skyline_far_strength','skyline_far_complexity')]:
        s=rcfg['skyline']['summed_angular_prominence_percentile']*percentile_score(frame[strength])+rcfg['skyline']['smoothed_complexity_percentile']*percentile_score(frame[complexity])
        add(label,frame.nps.to_numpy()+weights['skyline']*(s-frame.skyline.to_numpy()))
    upper=frame.copy();upper['visible_peak_ground_proxies']+=upper.unknown_peak_targets
    upper=component_scores(upper,rcfg)
    add('unknown_peak_count_upper_bound_only',weighted_score(upper,weights))
    rng=np.random.default_rng(rcfg['sensitivity']['seed'])
    draws=rng.dirichlet(base*rcfg['sensitivity']['dirichlet_concentration'],size=rcfg['sensitivity']['random_weight_draws'])
    scores=frame[COMPONENTS].to_numpy()@draws.T
    ranks=np.empty(scores.shape,dtype=np.int32);top_count=np.zeros(len(frame),int)
    for j in range(scores.shape[1]):
        order=stable_order(ids,scores[:,j]);ranks[order,j]=np.arange(1,len(frame)+1);top_count[order[:10]]+=1
    robustness=pd.DataFrame({'observer_id':ids,'top10_weight_frequency':top_count/len(draws),
        'weight_rank_p05':np.percentile(ranks,5,axis=1),'weight_rank_p95':np.percentile(ranks,95,axis=1),
        'weight_rank_min':ranks.min(axis=1),'weight_rank_max':ranks.max(axis=1)})
    named=pd.DataFrame({'observer_id':ids,**columns})
    return robustness,named,summary,draws


def run_rank(run):
    require_resources(config())
    rcfg=yaml.safe_load((PROJECT/'config/ranking.yaml').read_text(encoding='utf-8'))
    weights=yaml.safe_load((PROJECT/'config/weights.yaml').read_text(encoding='utf-8'))['nps']
    raw,audit=extract_and_audit(run,rcfg)
    output=PROJECT/'data/processed/g5';output.mkdir(parents=True,exist_ok=True)
    atomic_json(output/'g4_audit.json',audit)
    write_parquet(raw,output/'raw_metrics.parquet')
    frame=component_scores(raw,rcfg);frame['nps']=weighted_score(frame,weights)
    if frame[COMPONENTS+['nps']].isna().any().any():raise ValueError('Missing component: do not fabricate a complete NPS')
    if not frame[COMPONENTS+['nps']].apply(lambda s:s.between(0,100).all()).all():raise ValueError('Score outside 0-100')
    frame['mps']=np.nan;frame['mps_status']='unavailable_incomplete_nonlake_registry'
    frame['elevation_band']=pd.cut(frame.elevation_m,rcfg['elevation_bands_m'],right=False).astype(str)
    robustness,named,scenarios,draws=sensitivity(frame,weights,rcfg)
    frame=frame.merge(robustness,on='observer_id',validate='one_to_one')
    frame=frame.iloc[stable_order(frame.observer_id,frame.nps)].reset_index(drop=True)
    frame['position']=np.arange(1,len(frame)+1);frame['score_rank']=frame.nps.rank(method='min',ascending=False).astype(int)
    frame['band_position']=frame.groupby('elevation_band',observed=True).cumcount()+1
    write_parquet(frame,output/'rankings.parquet');frame.to_csv(output/'rankings.csv',index=False)
    frame.head(10).to_csv(output/'top10_nps.csv',index=False)
    frame[frame.band_position<=10].to_csv(output/'elevation_band_top10.csv',index=False)
    write_parquet(named,output/'sensitivity_ranks.parquet')
    pd.DataFrame(draws,columns=COMPONENTS).to_csv(output/'sampled_weights.csv',index=False)
    by_band=frame.groupby('elevation_band',observed=True).agg(count=('observer_id','size'),median_nps=('nps','median'),max_nps=('nps','max')).reset_index()
    by_band.to_csv(output/'elevation_band_summary.csv',index=False)
    winners={}
    for label,column,subset in [('largest_visible_area','visible_area_km2',frame),
        ('most_visible_peaks','visible_peak_ground_proxies',frame),('highest_skyline_component','skyline',frame),
        ('farthest_visible_peak_proxy','maximum_visible_peak_distance_km',frame),
        ('best_below_2500m','nps',frame[frame.elevation_m<2500])]:
        row=subset.sort_values([column,'observer_id'],ascending=[False,True]).iloc[0]
        winners[label]={'observer_id':row.observer_id,'name':row.display_name,'value':float(row[column]),'nps_position':int(row.position)}
    highest=frame.sort_values(['elevation_m','observer_id'],ascending=[False,True]).iloc[0]
    correlations={'spearman_elevation_nps':float(spearmanr(frame.elevation_m,frame.nps).statistic),
        'pearson_elevation_nps':float(pearsonr(frame.elevation_m,frame.nps).statistic),
        'spearman_dem_ground_nps':float(spearmanr(frame.ground_dem_m,frame.nps).statistic),
        'interpretation':'Descriptive for this mapped >=1800m cohort. Spatial dependence/nonrandom selection preclude naive iid significance; no p-values or causal claim.',
        'highest_observer':{'observer_id':highest.observer_id,'elevation_m':float(highest.elevation_m),'nps_position':int(highest.position)}}
    atomic_json(output/'correlation.json',correlations)
    atomic_json(output/'special_winners.json',winners)
    atomic_json(output/'sensitivity.json',{'named_scenarios':scenarios,'random_draws':len(draws),
        'seed':rcfg['sensitivity']['seed'],'caution':'Weight frequencies are robustness to chosen weights, not probability of a real-world best panorama. Unknown upper scenario bounds only the count input.'})
    summary={'passed':True,'observers':len(frame),'mps_available':False,'lake_visibility_in_ranking':False,
        'top10':frame.head(10)[['observer_id','display_name','elevation_m','nps','visible_area_km2','visible_peak_ground_proxies','top10_weight_frequency']].to_dict('records'),
        'correlations':correlations,'g4_audit':audit,'special_winners':winners,
        'named_scenario_top10_overlap_range':[min(s['top10_overlap'] for s in scenarios),max(s['top10_overlap'] for s in scenarios)],
        'inputs':{'g4_status_sha256':fingerprint(PROJECT/'data/processed/g4_status.json'),
            'ranking_config_sha256':fingerprint(PROJECT/'config/ranking.yaml'),'weights_sha256':fingerprint(PROJECT/'config/weights.yaml'),
            'algorithm_sha256':fingerprint(Path(__file__))},
        'outputs':{str(f.relative_to(PROJECT)):fingerprint(f) for f in output.iterdir() if f.is_file() and f.name!='summary.json'},
        'limitations':['GDAL ground-target proxies, not surveyed real-world views.',
            'Multi-scale skyline signal prominence is not topographic prominence; nearfield sensitivity retained.',
            'Only existing three-case 90m/30m pilot resolution comparison; full alternative-resolution rankings not calculated.',
            'Complete MPS unavailable; no zero landmark score imputed.']}
    atomic_json(output/'summary.json',summary)
    return summary
