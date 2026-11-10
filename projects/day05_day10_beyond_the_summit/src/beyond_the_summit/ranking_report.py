"""Validate and present G5 results without changing the frozen ranking method."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import spearmanr
import yaml

from .runtime import PROJECT,atomic_json,fingerprint,config,require_resources


def report_rankings():
    directory=PROJECT/'data/processed/g5'
    summary=json.loads((directory/'summary.json').read_text(encoding='utf-8'))
    inputs=summary['inputs']
    for key,path in [('g4_status_sha256',PROJECT/'data/processed/g4_status.json'),
                     ('ranking_config_sha256',PROJECT/'config/ranking.yaml'),('weights_sha256',PROJECT/'config/weights.yaml'),
                     ('algorithm_sha256',Path(__file__).with_name('ranking.py'))]:
        if fingerprint(path)!=inputs[key]:raise ValueError('G5 input or algorithm fingerprint changed')
    for path,digest in summary['outputs'].items():
        if fingerprint(PROJECT/path)!=digest:raise ValueError(f'G5 output fingerprint changed: {path}')
    frame=pd.read_parquet(directory/'rankings.parquet')
    if len(frame)!=1302 or frame.observer_id.nunique()!=1302 or not frame.nps.is_monotonic_decreasing:
        raise ValueError('Ranking count, IDs or ordering invalid')
    if frame[['terrain','peaks','skyline','distance','nps']].isna().any().any() or not frame.mps.isna().all():
        raise ValueError('Unexpected missing NPS or invented complete MPS')
    weights=yaml.safe_load((PROJECT/'config/weights.yaml').read_text(encoding='utf-8'))['nps']
    reconstructed=sum(frame[name]*weight for name,weight in weights.items())
    if not np.allclose(frame.nps,reconstructed,rtol=0,atol=1e-12):raise ValueError('Weighted score arithmetic does not reconcile')
    folder=PROJECT/'report/g5';folder.mkdir(parents=True,exist_ok=True)
    # Independent projection/edge QA pass, without new viewshed calculations.
    status=json.loads((PROJECT/'data/processed/g4_status.json').read_text(encoding='utf-8'))
    max_error=0.;max_geodesic=0.;beyond=0;edge_count=0
    for index,path in enumerate(status['completed_checkpoints'].values()):
        if index%100==0:require_resources(config())
        case=json.loads((PROJECT/path).read_text(encoding='utf-8'))
        edges_path=next(name for name in case['artifact_sha256'] if name.endswith('_edges.parquet'))
        edge=pd.read_parquet(PROJECT/edges_path,columns=['distance_projected_m','distance_geodesic_m'])
        if len(edge):
            max_error=max(max_error,float(np.abs(edge.distance_projected_m-edge.distance_geodesic_m).max()))
            max_geodesic=max(max_geodesic,float(edge.distance_geodesic_m.max()))
            beyond+=int((edge.distance_geodesic_m>100000).sum());edge_count+=len(edge)
    geometry={'edge_count':edge_count,'maximum_absolute_projected_vs_geodesic_m':max_error,
              'maximum_geodesic_target_range_m':max_geodesic,'targets_beyond_100km_geodesic_inside_projected_mask':beyond,
              'interpretation':'100 km is the explicit projected analysis mask; geodesic distances are reported separately. No silent radius substitution.'}
    atomic_json(folder/'projection_qa.json',geometry)
    groups=[]
    for ridge,part in frame.groupby('ridge_name',dropna=False):
        groups.append({'ridge_name':str(ridge),'count':len(part),
            'spearman_elevation_nps':float(spearmanr(part.elevation_m,part.nps).statistic) if len(part)>=10 else None,
            'interpretation':'descriptive within-ridge; not independent replicates'})
    pd.DataFrame(groups).to_csv(folder/'ridge_correlations.csv',index=False)
    top=frame.head(10)
    fig,axes=plt.subplots(1,2,figsize=(14,5),layout='constrained')
    scatter=axes[0].scatter(frame.elevation_m,frame.nps,s=12,c=frame.nearfield_horizon_fraction,
                           cmap='viridis',alpha=.6,linewidths=0)
    axes[0].scatter(top.elevation_m,top.nps,s=45,facecolors='none',edgecolors='#d95640',label='Baseline Top 10')
    axes[0].set(xlabel='Catalogue summit elevation (m)',ylabel='Exploratory NPS (0-100)',
                title=f"Elevation and NPS: Spearman rho={summary['correlations']['spearman_elevation_nps']:.3f}")
    axes[0].legend(fontsize=8);fig.colorbar(scatter,ax=axes[0],label='Horizon fraction limited within 500 m')
    bottom=np.zeros(len(top))
    for name,color in zip(weights,['#238a88','#ce9b36','#6b78b5','#b45a65']):
        values=top[name].to_numpy()*weights[name]
        axes[1].barh(np.arange(10),values,left=bottom,color=color,label=f'{name} ({weights[name]:.0%})');bottom+=values
    axes[1].set_yticks(np.arange(10),top.observer_id);axes[1].invert_yaxis()
    axes[1].set(xlabel='Weighted component contribution',title='Baseline NPS Top 10')
    axes[1].legend(fontsize=8,loc='lower right');axes[1].set_xlim(0,100)
    fig.savefig(folder/'rankings.png',dpi=160);plt.close(fig)
    fig,axis=plt.subplots(figsize=(11,5),layout='constrained')
    axis.barh(np.arange(10),top.top10_weight_frequency.to_numpy()*100,color='#238a88')
    axis.set_yticks(np.arange(10),top.observer_id);axis.invert_yaxis()
    axis.set(xlim=(0,100),xlabel='In Top 10 across sampled weights (%)',
             title='Weight robustness: 500 reproducible draws, not probability of a true best view')
    for i,value in enumerate(top.top10_weight_frequency):axis.text(min(value*100+1,96),i,f'{value:.1%}',va='center',fontsize=8)
    fig.savefig(folder/'weight_robustness.png',dpi=160);plt.close(fig)
    scenarios=json.loads((directory/'sensitivity.json').read_text(encoding='utf-8'))['named_scenarios']
    small=[s['top10_overlap'] for s in scenarios if '20pct' in s['scenario']]
    highest=summary['correlations']['highest_observer'];first=top.iloc[0];second=top.iloc[1]
    audit=summary['g4_audit']
    rows=[f"| {int(r.position)} | {r.observer_id} | {r.display_name} | {r.elevation_m:.1f} | {r.nps:.2f} | {r.visible_area_km2:.1f} | {int(r.visible_peak_ground_proxies)} | {r.top10_weight_frequency:.1%} |"
          for r in top.itertuples()]
    scenario_rows=[f"| {s['scenario']} | {s['top10_overlap']}/10 | {s['winner']} | {s['spearman_with_baseline']:.4f} |" for s in scenarios]
    winners='\n'.join(f"- {name}: {value['name']} ({value['observer_id']}), value {value['value']:.3f}; NPS position {value['nps_position']}." for name,value in summary['special_winners'].items())
    text=f'''# G5: verified results and exploratory panorama ranking

2026-11-10, Asia/Tashkent. **G4 completed and verified for all 1,302 summits. G5 natural panorama rankings are calculated.** Complete MPS remains unavailable; no missing landmark contribution was replaced with zero. Lakes remain excluded. No publication or deployment occurred.

## G4 verification

All **{audit['verified_artifact_files']:,} artifact hashes** matched ({audit['verified_bytes']/2**30:.2f} GiB checked). Observer IDs, aggregate/individual metrics, projected raster schemas, distance-band denominators, peak edge identities/counts and signed skyline schemas reconcile. No source/model/environment mismatch was found.

**{audit['unknown_peak_observations']} unknown peak observations** affect {audit['observers_with_unknown_targets']} observers at the exact projected radius mask boundary. Their edge values remain unknown; known visible counts are lower bounds, not proof those unknown targets are hidden. The count-upper sensitivity retained the same Top 10 in this cohort.

Independent same-DSM LOS: {audit['los_count']:,} checks, {audit['non_grazing_los_count']:,} non-grazing with **{audit['non_grazing_agreement']:.2%} agreement**; near-grazing agreement {audit['near_grazing_agreement']:.2%}. These are deterministic diagnostic rays, not unbiased accuracy or ground truth. Earlier engine-comparison limitations remain in force.

## Frozen score

NPS=30% terrain +25% visible peaks +30% skyline +15% distance/relative angular relief. The full [method](g5_methodology.md), `config/ranking.yaml` and `config/weights.yaml` were fixed before scoring. Normalization is cohort-relative with zero evidence anchored at zero; missing values are not imputed. Skyline signal prominence is computed at 0.5/1/2-degree smoothing scales and is distinct from topographic prominence. Scores use unrounded values; IDs resolve presentation ties.

## Baseline Top 10

| Position | Stable ID | Name or ID fallback | Elevation (m) | NPS | Visible terrain (km2) | Known visible peak proxies | Top-10 weight frequency |
|---|---|---|---:|---:|---:|---:|---:|
{chr(10).join(rows)}

Missing names remain stable IDs rather than invented mountain names. Baseline first and second differ by only **{first.nps-second.nps:.3f} points**; this is not evidence of a uniquely best real-world summit.

![Scores and components](../report/g5/rankings.png)

## Does higher mean better?

- Spearman elevation/NPS: **{summary['correlations']['spearman_elevation_nps']:.3f}**.
- Pearson elevation/NPS: **{summary['correlations']['pearson_elevation_nps']:.3f}**.
- Spearman using effective DEM ground instead of catalogue elevation: **{summary['correlations']['spearman_dem_ground_nps']:.3f}**.
- Highest observer, **{highest['observer_id']} at {highest['elevation_m']:.1f} m**, ranks **{highest['nps_position']}** under the baseline NPS.

There is a positive relationship in this mapped >=1,800 m cohort, but elevation does not determine this score. This is a descriptive spatial/nonrandom cohort comparison, not a causal claim or a statement about all regional summits. No naive iid p-values are reported. Existing mixed OSM/DEM elevation provenance is retained. Within-ridge descriptive correlations are in `report/g5/ridge_correlations.csv`.

## Robustness

Eight modest +/-20% relative weight changes preserve **{min(small)}-{max(small)} of 10** baseline Top-10 members. Further weight and skyline scenarios preserve **{min(s['top10_overlap'] for s in scenarios)}-10**. First place changes in several plausible scenarios. Five hundred reproducible Dirichlet draws report weight-induced rank ranges and Top-10 frequencies; these are not confidence intervals or probabilities of actual panorama quality.

![Weight robustness](../report/g5/weight_robustness.png)

| Scenario | Baseline Top-10 retained | Winner | Score-order Spearman |
|---|---:|---|---:|
{chr(10).join(scenario_rows)}

Nearfield skyline features remain in baseline; the explicit 500 m ablation demonstrates sensitivity to nearby terrain. No method was retuned after seeing winners. The earlier three-case 90m/30m pilot is the available DEM-resolution sensitivity evidence; no complete alternate-resolution ranking was computed or claimed.

## Special categories

{winners}

These are metric-specific winners, not necessarily the overall score winner. Farthest-peak values are geometric ground proxies; angular relief is not measured optical recognizability.

## Radius and projection QA

Across {edge_count:,} target observations, maximum absolute projected/geodesic distance difference is **{max_error:.2f} m**. The explicit computation limit is **100 km projected**. {beyond} target observations have reported geodesic distance slightly above 100 km, with maximum **{max_geodesic/1000:.5f} km**; this is documented projection distortion, not a 150 km scenario. Geometry details: `report/g5/projection_qa.json`.

## Outputs and remaining gaps

- `data/processed/g5/rankings.parquet` and `rankings.csv`: all 1,302 raw, normalized, component, NPS, rank and robustness fields; MPS missing with an explicit reason.
- `top10_nps.csv`, `elevation_band_top10.csv`, `elevation_band_summary.csv`: globally normalized overall/elevation-band results.
- `raw_metrics.parquet`, `g4_audit.json`: preserved measured evidence and checks.
- `sensitivity_ranks.parquet`, `sampled_weights.csv`, `sensitivity.json`: all named/500 sampled weight scenarios.
- `correlation.json`, `special_winners.json`, `summary.json`: machine-readable findings/provenance.
- `report/g5/`: real generated figures and projection/within-ridge QA.

The complete non-lake MPS registry still needs official membership/coordinate and visual-eligibility checks; **all 1,302 MPS values remain missing**. Lake geometry is not a blocker because lakes are excluded by user decision. NPS is an exploratory raster/OSM-based score, not verified field visibility, navigation guidance or a definitive aesthetic judgement. Full publication reports and website remain G6; no commit or deployment is authorized.
'''
    (PROJECT/'docs/g5_checkpoint.md').write_text(text,encoding='utf-8')
    validation={'passed':True,'rows':len(frame),'nps_finite_and_reconciled':True,'mps_missing_rows':int(frame.mps.isna().sum()),
        'source_and_output_fingerprints_valid':True,'g4_audit':audit,'projection_qa':geometry,
        'lake_visibility_in_ranking':False,'report':'docs/g5_checkpoint.md'}
    atomic_json(directory/'validation.json',validation)
    return {'passed':True,'report':'docs/g5_checkpoint.md','winner':first.observer_id,
        'spearman_elevation_nps':summary['correlations']['spearman_elevation_nps'],'mps_available':False}
