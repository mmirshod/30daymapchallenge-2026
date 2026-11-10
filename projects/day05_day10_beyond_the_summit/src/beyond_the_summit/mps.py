"""Small, reproducible Horizon-only MPS extension of immutable G4/G5 products."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
import geopandas as gpd
import yaml
from .runtime import PROJECT, config, require_resources, fingerprint, atomic_json

# Reviewed official roster positions, including spelling/transliteration aliases.
ORDINALS = {
    'node:3328009998':1, 'node:2353039433':2, 'node:1423812498':3,
    'node:1227626171':4, 'node:2556642796':5, 'node:1705630558':6,
    'node:1411929292':7, 'node:1423818567':9, 'node:2574164671':10,
    'node:2556670537':12, 'node:2556670543':13, 'node:2576589389':14,
    'node:1411914577':19, 'node:2556670609':20, 'node:2556656114':21,
}

def landmark_score(count, distance_sum, relief_sum, denominator=15):
    """Fixed coverage denominator; zero visible scores zero, no renormalization."""
    if denominator <= 0: raise ValueError('Positive denominator required')
    return 100*(.70*count+.15*distance_sum+.15*relief_sum)/denominator

def main():
    cfg=config();require_resources(cfg)
    root=PROJECT/'data/processed';out=root/'mps';out.mkdir(exist_ok=True)
    method=yaml.safe_load((PROJECT/'config/mps.yaml').read_text())
    # This version is frozen; do not silently accept unsupported formula edits.
    assert method['landmark_weights']=={'count':.70,'distance':.15,'angular_relief':.15}
    assert method['natural_weight']==.8 and method['landmark_weight']==.2
    assert method['distance_scale_m']==100000 and method['angular_relief_scale_degrees']==1
    source=root/'g5/rankings.parquet';scores=pd.read_parquet(source)
    landmarks=gpd.read_parquet(root/'landmarks_audited.parquet')
    targets=gpd.read_parquet(root/'target_peaks.parquet')
    roster=json.loads((root/'official_landmark_rosters.json').read_text(encoding='utf8'))['entries']
    official={r['ordinal']:r['text'] for r in roster if r['program']=='Horizon'}
    registry=[]
    for _,r in landmarks[landmarks.program.eq('Horizon')&landmarks.within_analysis_scope].iterrows():
        distances=targets.geometry.distance(r.geometry);j=distances.idxmin();t=targets.loc[j]
        if distances[j]>1 or t.target_id not in ORDINALS:raise ValueError('Unreviewed landmark identity')
        registry.append({'landmark_id':r.landmark_id,'name':r['name'],'target_id':t.target_id,
            'official_ordinal':ORDINALS[t.target_id],'official_text':official[ORDINALS[t.target_id]],
            'coordinate_difference_m':float(distances[j]),'membership_evidence':'user GPX + reviewed official name/alias',
            'x':t.geometry.x,'y':t.geometry.y})
    registry=pd.DataFrame(registry)
    assert len(registry)==method['denominator']==15 and registry.target_id.is_unique
    registry.to_csv(out/'horizon_registry.csv',index=False,encoding='utf-8-sig')
    ids=set(registry.target_id);rows=[];observations=[];inputs={str(source.relative_to(PROJECT)):fingerprint(source)}
    for index,r in scores.iterrows():
        if index%50==0:require_resources(cfg)
        marker_path=PROJECT/r.checkpoint;marker=json.loads(marker_path.read_text())
        rel=next(k for k in marker['artifact_sha256'] if k.endswith('_edges.parquet'))
        path=PROJECT/rel
        if fingerprint(path)!=marker['artifact_sha256'][rel]:raise ValueError('G4 edge hash mismatch')
        inputs[rel]=marker['artifact_sha256'][rel]
        edges=pd.read_parquet(path);edges=edges[edges.target_id.isin(ids)].copy()
        expected=registry[np.hypot(registry.x-r.x,registry.y-r.y)<=100000]
        expected=set(expected.target_id)-{r.observer_id}
        if set(edges.target_id)!=expected or not edges.target_id.is_unique:raise ValueError('Missing/duplicate landmark edge')
        d=edges.distance_projected_m.to_numpy()
        angle=np.degrees(np.arctan2(edges.target_ground_dem_m.to_numpy()-r.ground_dem_m-1.7-(1-.14286)*d*d/(2*6378137),d))
        relief=np.clip(angle,0,1);distance=np.clip(d/100000,0,1)
        visible=edges.visible.fillna(False).to_numpy(dtype=bool);unknown=edges.visible.isna().to_numpy()
        lower=landmark_score(visible.sum(),distance[visible].sum(),relief[visible].sum())
        upper=landmark_score((visible|unknown).sum(),distance[visible|unknown].sum(),relief[visible|unknown].sum())
        rows.append({'observer_id':r.observer_id,'visible_horizon_count':int(visible.sum()),
            'unknown_horizon_count':int(unknown.sum()),'landmark_score_lower':lower,'landmark_score_upper':upper,
            'landmark_count_only':100*visible.sum()/15,'mps':.8*r.nps+.2*lower,
            'mps_upper':.8*r.nps+.2*upper,'mps_status':'conservative_unknown_bounds' if unknown.any() else 'complete_exploratory_horizon'})
        edges['angular_relief_degrees']=angle;observations.append(edges)
    result=scores.drop(columns=['mps','mps_status']).merge(pd.DataFrame(rows),on='observer_id',validate='one_to_one')
    result=result.sort_values(['mps','observer_id'],ascending=[False,True]).reset_index(drop=True)
    result['mps_position']=np.arange(1,len(result)+1)
    result['rank_gain_vs_nps']=result.position-result.mps_position
    result['mps_count_only']=.8*result.nps+.2*result.landmark_count_only
    for w in [.1,.3]:result[f'mps_landmark_weight_{int(w*100)}']=(1-w)*result.nps+w*result.landmark_score_lower
    assert len(result)==1302 and result.mps.between(0,100).all()
    assert (result.mps_upper>=result.mps-1e-12).all()
    result.to_parquet(out/'rankings.parquet',index=False)
    result.to_csv(out/'rankings.csv',index=False,encoding='utf-8-sig')
    result.head(10).to_csv(out/'top10_mps.csv',index=False,encoding='utf-8-sig')
    pd.concat(observations,ignore_index=True).to_parquet(out/'horizon_visibility.parquet',index=False)
    baseline=set(result.head(10).observer_id);sensitivity={}
    for col in ['mps_count_only','mps_landmark_weight_10','mps_landmark_weight_30']:
        top=result.sort_values([col,'observer_id'],ascending=[False,True]).head(10)
        sensitivity[col]={'top10_overlap':len(baseline&set(top.observer_id)),'winner':top.iloc[0].observer_id}
    summary={'status':'complete','observers':len(result),'landmarks':15,
        'observers_with_unknown':int((result.unknown_horizon_count>0).sum()),
        'maximum_visible_landmarks':int(result.visible_horizon_count.max()),
        'winner':result.iloc[0][['observer_id','mps','nps','visible_horizon_count','position']].to_dict(),
        'sensitivity':sensitivity,'inputs':inputs,
        'method_sha256':fingerprint(PROJECT/'config/mps.yaml'),'code_sha256':fingerprint(Path(__file__)),
        'registry_inputs':{name:fingerprint(root/name) for name in ['landmarks_audited.parquet','target_peaks.parquet','official_landmark_rosters.json','mps_scope_clarification.json']},
        'outputs':{f.name:fingerprint(f) for f in out.iterdir() if f.suffix in ['.csv','.parquet']}}
    atomic_json(out/'summary.json',summary)
    print(json.dumps({k:v for k,v in summary.items() if k not in ['inputs','outputs','registry_inputs']},ensure_ascii=True))

if __name__=='__main__':main()
