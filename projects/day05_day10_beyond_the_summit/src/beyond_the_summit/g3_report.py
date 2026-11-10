"""Build reviewable tables and figures from measured G3 artifacts."""
from __future__ import annotations

import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from .runtime import PROJECT, atomic_json


def report_g3():
    measured=PROJECT/'data/processed/g3_benchmark_measured.json'
    current=json.loads((PROJECT/'data/processed/g3_benchmark.json').read_text(encoding='utf-8'))
    original=json.loads(measured.read_text(encoding='utf-8')) if measured.exists() else current
    if current['status']!='complete' or original['status']!='complete' or current['signature']!=original['signature']:
        raise RuntimeError('Finish a consistent G3 benchmark before generating its report')
    cases=original['cases'];folder=PROJECT/'report/g3';folder.mkdir(parents=True,exist_ok=True)
    records=[]
    for case in cases:
        records.append({'observer_id':case['observer']['observer_id'],
            'elevation_m':case['observer']['elevation_m'],**case['timings'],
            'visible_area_km2':case['terrain']['visible_area_km2'],
            'visible_peak_proxies':case['peaks']['visible_peak_ground_proxies'],
            'eligible_targets':case['peaks']['eligible_targets_in_radius'],
            'non_grazing_los_count':case['los']['non_grazing_count'],
            'non_grazing_los_agreement':case['los']['non_grazing_agreement_fraction']})
    frame=pd.DataFrame(records);frame.to_csv(folder/'observer_timings.csv',index=False)
    fig,axes=plt.subplots(4,3,figsize=(15,10),sharex=True,layout='constrained')
    for axis,case in zip(axes.flat,cases):
        h=json.loads((PROJECT/case['horizon']).read_text(encoding='utf-8'))
        bearing=np.array(h['azimuth_true_degrees']);order=np.argsort(bearing)
        axis.plot(bearing[order],np.array(h['horizon_degrees'])[order],color='#187e80',linewidth=.65)
        axis.axhline(0,color='gray',linewidth=.5)
        axis.set_title(case['observer']['observer_id'],fontsize=9)
        axis.set_xlim(0,360);axis.set_xticks([0,90,180,270,360]);axis.grid(alpha=.15)
    fig.supylabel('Signed horizon elevation (degrees)');fig.supxlabel('True bearing to limiting terrain point (degrees)')
    fig.suptitle('G3: twelve 100 km / 30 m skyline profiles (0.1 degree grid sampling)')
    fig.savefig(folder/'horizons.png',dpi=150);plt.close(fig)
    stages=[('adapter_total_seconds','GDAL adapter incl. window preparation'),
            ('terrain_summary_seconds','Terrain summary'),('target_summary_seconds','Peak summary'),
            ('skyline_and_los_seconds','Skyline + LOS diagnostics')]
    fig,ax=plt.subplots(figsize=(12,5),layout='constrained');bottom=np.zeros(len(frame))
    for column,label in stages:
        values=frame[column].to_numpy();ax.bar(np.arange(1,len(frame)+1),values,bottom=bottom,label=label);bottom+=values
    ax.set(xlabel='Observer number (saved pilot order)',ylabel='Measured seconds',xticks=np.arange(1,len(frame)+1),
           title='G3 per-observer stages: core GDAL time is included inside the adapter')
    ax.legend(fontsize=8,loc='lower center',bbox_to_anchor=(.5,1.01),ncol=2)
    ax.set_title('G3 per-observer stages: core GDAL time is included inside the adapter',pad=48)
    fig.savefig(folder/'stage_timings.png',dpi=150);plt.close(fig)
    events=[json.loads(line) for line in (PROJECT/'logs/runs'/f"{original['run_id']}.jsonl").read_text(encoding='utf-8').splitlines()]
    finish=next(e for e in reversed(events) if e['event']=='finish')
    estimate=original['full_cohort_estimate'];rows=[]
    for c in cases:
        ng=c['los']['non_grazing_agreement_fraction']
        rows.append(f"| {c['observer']['observer_id']} | {c['timings']['gdal_compute_initial_output_seconds']:.2f} | "
            f"{c['timings']['case_wall_seconds']:.2f} | {c['terrain']['visible_area_km2']:.2f} | "
            f"{c['peaks']['visible_peak_ground_proxies']} | {ng:.1%} |" if ng is not None else
            f"| {c['observer']['observer_id']} | - | - | - | - | no non-grazing sample |")
    text=f'''# G3: end-to-end GDAL benchmark

2026-11-10, Asia/Tashkent. **All {len(cases)} saved observers completed at 100 km / 30 m, sequentially.** Lakes are excluded from ranking and were not sampled for visibility. No full-cohort analysis or ranking was started.

## Measured execution

Original invocation: **{original['invocation_wall_seconds']:.2f} seconds** inside the benchmark, {finish['wall_seconds']:.2f} seconds for its enclosing logged command. Cases include window validation/preparation, isolated GDAL execution, exact-radius masking, terrain/distance/direction summaries, peak edges, 0.1-degree signed skyline extraction, non-lake landmark point diagnostics and independent LOS checks.

| Observer | GDAL core/output (s) | End-to-end case (s) | Visible terrain (km2) | Visible peak ground proxies | Non-grazing LOS agreement |
|---|---:|---:|---:|---:|---:|
{chr(10).join(rows)}

Median stage times: GDAL core **{frame.gdal_compute_initial_output_seconds.median():.2f}s**, complete GDAL adapter **{frame.adapter_total_seconds.median():.2f}s**, terrain summary **{frame.terrain_summary_seconds.median():.2f}s**, target summary **{frame.target_summary_seconds.median():.2f}s**, skyline/LOS **{frame.skyline_and_los_seconds.median():.2f}s**. Adapter costs include startup, terrain validation, compressed scratch writing, exact mask and provenance hashes; the 0.8-second independent pilot was not an end-to-end timing.

![Measured stages](../report/g3/stage_timings.png)

## Cost and resource interpretation

Median measured case: **{estimate['median_case_seconds']:.2f}s**. Linear scaling to 1,302 observers gives **{estimate['median_scaled_hours']:.2f} hours**, with a sampled min/max scaling span of **{estimate['min_max_scaled_hours'][0]:.2f}-{estimate['min_max_scaled_hours'][1]:.2f} hours**. This is an estimate, not a confidence interval or promised runtime. It includes the benchmark's target/skyline/LOS work, but excludes publication, additional analyses, retries, sleep/breaks and initial cohort loading. Faster scratch/window preparation is a possible next optimization, not an already measured improvement.

Sampled command process-tree RSS peaked at **{finish['peak_process_tree_rss_bytes']/2**20:.1f} MiB**; minimum available physical RAM was **{finish['minimum_available_ram_bytes']/2**30:.2f} GiB**. Native resource safeguards stayed active. Per-invocation RAM entry was 2 GiB as explicitly authorized; production defaults remain 4 GiB. The 2 GiB runtime RAM/commit and 15 GiB disk reserves were preserved. Process RSS sampling may count shared pages more than once and can miss very brief peaks.

## Output interpretation and limitations

Terrain area uses projected cell area and a 100 km projected cell-centre mask. Peaks are zero-target-height GDAL raster-ground proxies sampled at catalogue coordinates; surveyed summit heights are not silently substituted. Self edges are excluded. Edge tables preserve model distances, geodesic distances, true bearings and unknown mask-boundary cases.

There are {sum(c['peaks']['unknown_targets'] for c in cases)} unknown target observations at the exact raster mask boundary; they remain unknown rather than being converted to hidden. No terrain cells inside the mask are unknown. Stored G3 case artifacts total {sum((PROJECT/name).stat().st_size for c in cases for name in c['artifact_sha256'])/2**20:.1f} MiB (plus checkpoint metadata). Maximum sampled native scratch was {max(c['native_measurements']['peak_sampled_scratch_bytes'] for c in cases)/2**20:.1f} MiB, including the shared monitored workspace temporary tree.

Skyline rays use the effective observer cell, half-cell radial spacing, curvature coefficient 1-k and WGS84 semimajor radius. Negative horizons remain valid. Each limiting point has projected coordinates and a geodesic bearing. Local angular contrast uses a provisional 0.5-degree circular smoothing / +/-5-degree minimum baseline; it is not topographic prominence or a finalized normalized ranking score.

![Signed skyline profiles](../report/g3/horizons.png)

Independent LOS checks: **{original['los_count']} total**, **{original['non_grazing_los_count']} non-grazing**, non-grazing agreement **{original['non_grazing_los_agreement']:.2%}**. Targets were selected deterministically across GDAL class/distance strata and supplemented to 24 rays per observer. This same-DSM target sample is not unbiased accuracy or ground truth, and does not erase the earlier GDAL/GRASS discrepancies from different terrain samples. Grazing checks remain separate and retained.

All 24 supplied lake waypoints remain in source audit files for provenance, with explicit ranking exclusion. Lake polygons and lake visibility are no longer required. Non-lake landmark diagnostics are unverified point proxies only; remaining official membership/missing-coordinate/visual-eligibility gaps still prevent a complete MPS. No NPS or MPS score was invented.

## Checkpoints and validation

Every observer has atomic metrics/checkpoint JSON, a GDAL raster/manifest, sparse Parquet peak edges, skyline JSON and independent LOS JSON under `data/interim/g3/{original['signature'][:16]}/`. Checkpoints bind inputs, config, environment, algorithms and artifact hashes. Completed outputs are reused only after validation; stale/interrupted/corrupt checkpoints are rejected.

Current replay: {current['resumed_cases']} of 12 validated case checkpoints reused; invocation {current['invocation_wall_seconds']:.2f}s. Original measured costs remain saved separately in `data/processed/g3_benchmark_measured.json`; replay costs do not replace fresh-run scaling evidence. Restart/failure/stale/corrupt artifact behavior and reserves have automated tests. Prior G1 integration passed with the explicit lower-entry override, and the pre-benchmark full suite passed 45 tests with no skips.

CSV timings: `report/g3/observer_timings.csv`. Machine summaries: `data/processed/g3_benchmark_measured.json` and `data/processed/g3_benchmark.json`. This checkpoint does not authorize 1,302-observer production, commits, Drive uploads or deployment.
'''
    (PROJECT/'docs/g3_checkpoint.md').write_text(text,encoding='utf-8')
    atomic_json(PROJECT/'data/processed/g3_report.json',{'signature':original['signature'],
        'measured_run_id':original['run_id'],'replay_run_id':current['run_id'],
        'report':'docs/g3_checkpoint.md','figures':['report/g3/horizons.png','report/g3/stage_timings.png']})
    return {'report':'docs/g3_checkpoint.md','case_count':len(cases),'median_scaled_hours':estimate['median_scaled_hours']}
