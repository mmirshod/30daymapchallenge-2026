"""Render a factual pilot checkpoint from recorded artifacts, without scoring."""
from __future__ import annotations
from datetime import datetime,timezone
import json
from pathlib import Path
import statistics
import numpy as np
from .runtime import PROJECT,atomic_json,resource_snapshot


def summarize_pilot() -> dict:
    reports={}
    for phase in ['local','100km','100km30']:
        path=PROJECT/f'data/processed/pilot_{phase}.json'
        if path.exists():reports[phase]=json.loads(path.read_text(encoding='utf-8'))
    summary={'timestamp_utc':datetime.now(timezone.utc).isoformat(),'resources':resource_snapshot(),
             'phases':{},'resolution_comparisons':[],'production_approved':False}
    for phase,report in reports.items():
        cases=report['cases'];profiles=[r for c in cases for r in c['los']['profiles']]
        clear=[r for r in profiles if not r['near_grazing_2m']]
        times=[c['timing']['wall_seconds'] for c in cases]
        scratch=[c['timing']['peak_sampled_scratch_bytes'] for c in cases if 'peak_sampled_scratch_bytes' in c['timing']]
        summary['phases'][phase]={'cases':len(cases),'radius_m':report['radius_m'],
            'native_wall_seconds_min':min(times),'native_wall_seconds_median':statistics.median(times),
            'native_wall_seconds_max':max(times),
            'peak_native_process_tree_rss_bytes':max(c['timing']['peak_process_tree_rss_bytes'] for c in cases),
            'peak_sampled_scratch_bytes':max(scratch) if scratch else None,
            'profiles':len(profiles),'point_reference_agreement_fraction':sum(r['agrees'] for r in profiles)/len(profiles),
            'non_grazing_profiles':len(clear),'point_reference_non_grazing_agreement_fraction':sum(r['agrees'] for r in clear)/len(clear) if clear else None,
            'serial_native_only_hours_for_1302':statistics.median(times)*1302/3600}
        cell=[r for c in cases if c.get('los_cell_reference') for r in c['los_cell_reference']['profiles'] if not r['near_grazing_2m']]
        if cell:summary['phases'][phase]['cell_reference_non_grazing_agreement_fraction']=sum(r['agrees'] for r in cell)/len(cell)
    if '100km' in reports and '100km30' in reports:
        coarse={c['observer']['observer_id']:c for c in reports['100km']['cases']}
        for fine in reports['100km30']['cases']:
            ident=fine['observer']['observer_id'];c=coarse[ident]
            comparison={'observer_id':ident,'visible_area_30m_km2':fine['visible_area_km2'],
                'visible_area_90m_km2':c['visible_area_km2'],
                'relative_area_change_90_vs_30':(c['visible_area_km2']-fine['visible_area_km2'])/fine['visible_area_km2'],
                'horizon_convergence':{}}
            if fine.get('horizons'):
                reference=json.loads((PROJECT/fine['horizons']['0.05']['path']).read_text(encoding='utf-8'))
                for step in ['0.25','0.1']:
                    profile=json.loads((PROJECT/fine['horizons'][step]['path']).read_text(encoding='utf-8'))
                    interpolated=np.interp(reference['azimuth_grid_north_degrees'],profile['azimuth_grid_north_degrees'],profile['horizon_degrees'],period=360)
                    errors=np.abs(interpolated-reference['horizon_degrees'])
                    comparison['horizon_convergence'][step]={'p95_interpolated_error_degrees':float(np.percentile(errors,95)),
                        'max_interpolated_error_degrees':float(errors.max())}
            summary['resolution_comparisons'].append(comparison)
    atomic_json(PROJECT/'data/processed/pilot_summary.json',summary)
    lines=['# Pilot results — 2026-11-09','',
        'Study: 1,302 mapped Tashkent summits >=1,800 m; 100 km maximum radius; one observer at a time. These are benchmark and diagnostic results, not panorama scores or rankings.','',
        '| Phase | Observers | Native wall seconds min / median / max | Peak sampled native process-tree RSS | Peak sampled scratch |',
        '|---|---:|---:|---:|---:|']
    for phase,s in summary['phases'].items():
        scratch_label=f"{s['peak_sampled_scratch_bytes']/2**30:.2f} GiB" if s['peak_sampled_scratch_bytes'] is not None else 'not recorded'
        lines.append(f"| {phase} | {s['cases']} | {s['native_wall_seconds_min']:.2f} / {s['native_wall_seconds_median']:.2f} / {s['native_wall_seconds_max']:.2f} | {s['peak_native_process_tree_rss_bytes']/2**20:.0f} MiB | {scratch_label} |")
    lines+=['','Native wall time includes fresh GRASS startup, DEM import, viewshed and export. It excludes Python profile diagnostics, skyline checks and acquisition. Scratch is sampled every three seconds and RSS every half second; these are sampled peaks. Process-tree RSS sums working sets and can include shared pages more than once.','',
        '## Independent profile checks','',
        'Point-reference diagnostics use the supplied summit XY and bilinear DEM ground. GRASS models the containing raster-cell centre. Cell-reference diagnostics use the cell centre and WGS84 semimajor axis to match that convention. Original summit coordinates are retained; the difference is not silently treated as a summit relocation. Both remain same-DEM tests, not surveyed ground truth. The +/-2 m grazing band is diagnostic.','']
    for phase,s in summary['phases'].items():
        lines.append(f"- {phase}: {s['profiles']} profiles; point-reference agreement {s['point_reference_agreement_fraction']:.2%}; non-grazing agreement {s['point_reference_non_grazing_agreement_fraction']:.2%} across {s['non_grazing_profiles']} profiles.")
        if 'cell_reference_non_grazing_agreement_fraction' in s:lines.append(f"  Matched cell-reference non-grazing agreement: {s['cell_reference_non_grazing_agreement_fraction']:.2%}.")
    lines+=['','## Resolution comparison','',
        '| Observer | Visible terrain at 30 m | Visible terrain at 90 m | 90 m relative change |',
        '|---|---:|---:|---:|']
    for c in summary['resolution_comparisons']:
        lines.append(f"| {c['observer_id']} | {c['visible_area_30m_km2']:.1f} km² | {c['visible_area_90m_km2']:.1f} km² | {c['relative_area_change_90_vs_30']:+.1%} |")
    if summary['resolution_comparisons']:
        median_change=statistics.median(abs(c['relative_area_change_90_vs_30']) for c in summary['resolution_comparisons'])
        summary['median_absolute_area_change_90_vs_30']=median_change
        summary['provisional_10pct_area_gate_passed']=median_change<=.10
        lines+=['',f'Median absolute visible-area change: **{median_change:.1%}**; provisional <=10% gate: **{"PASS" if median_change<=.10 else "FAIL"}**. Three matched cases cannot establish ranking stability.']
        lines+=['','| Observer | Angular step | P95 difference from interpolated fine profile | Maximum difference |','|---|---:|---:|---:|']
        for c in summary['resolution_comparisons']:
            for step,error in c['horizon_convergence'].items():
                lines.append(f"| {c['observer_id']} | {step}° | {error['p95_interpolated_error_degrees']:.3f}° | {error['max_interpolated_error_degrees']:.3f}° |")
    lines+=['','Angular convergence compares circularly interpolated coarse horizons against 0.05-degree profiles. Diagnostic azimuths are grid-north; production true-bearing conversion, skyline prominence, smoothing and metric definitions still require validation.','',
        '## Cost interpretation and remaining gates','']
    gdal_path=PROJECT/'data/processed/pilot_gdal.json'
    if gdal_path.exists():
        import rasterio
        comparison=json.loads(gdal_path.read_text(encoding='utf-8'));engine=[]
        grass={c['observer']['observer_id']:c for c in reports.get('100km30',{}).get('cases',[])}
        lines+=['','### Independent GDAL comparison','',
            '| Observer | GDAL compute/output | Visible-pixel intersection over union with GRASS | Cell-reference non-grazing LOS agreement |',
            '|---|---:|---:|---:|']
        for case in comparison['cases']:
            prior=grass[case['observer']['observer_id']];x=case['observer']['x'];y=case['observer']['y'];tp=fp=fn=0
            with rasterio.open(PROJECT/case['output']) as a,rasterio.open(PROJECT/prior['output']) as b:
                if a.transform!=b.transform or a.shape!=b.shape:raise ValueError('Engine comparison grids differ')
                for _,w in a.block_windows(1):
                    aa=a.read(1,window=w);bb=b.read(1,window=w)
                    xx=a.transform.c+(w.col_off+np.arange(w.width)+.5)*a.res[0]
                    yy=a.transform.f-(w.row_off+np.arange(w.height)+.5)*a.res[1]
                    inside=np.hypot(xx[None,:]-x,yy[:,None]-y)<=100000
                    tp+=int(np.sum(inside&(aa==1)&(bb==1)))
                    fp+=int(np.sum(inside&(aa==1)&(bb==0)));fn+=int(np.sum(inside&(aa==0)&(bb==1)))
            iou=tp/(tp+fp+fn) if tp+fp+fn else None
            item={'observer_id':case['observer']['observer_id'],
                'compute_and_output_seconds':case['compute_and_output_seconds'],'visible_pixel_iou':iou,
                'cell_reference_non_grazing_agreement_fraction':case['cell_reference_los']['non_grazing_agreement_fraction']}
            engine.append(item)
            lines.append(f"| {item['observer_id']} | {item['compute_and_output_seconds']:.2f} s | {iou:.2%} | {item['cell_reference_non_grazing_agreement_fraction']:.2%} |")
        summary['gdal_crosscheck']=engine
        lines+=['','GDAL timing covers compute and initial output only, not common-grid alignment, Python diagnostics or summit/landmark calculations. The fast result is not accepted solely on speed or whole-circle pixel agreement. Visible-pixel IoU emphasizes the small visible subset; GRASS itself is a model reference, not ground truth. Production backend remains unchanged.','']
    for phase in ['100km','100km30']:
        if phase in summary['phases']:
            s=summary['phases'][phase]
            lines.append(f"- {phase}: scaling the measured median native time to 1,302 observers gives **{s['serial_native_only_hours_for_1302']:.1f} hours for the native terrain stage alone**. This is an extrapolation from {s['cases']} cases, not a measured full-run duration; it excludes skyline, peak/landmark LOS, retries and publication.")
    lines+=['- No baseline resolution or full production run is approved by this report. Check area differences against the provisional 10% threshold and independent non-grazing profiles against 99%; retain failed thresholds rather than relaxing them.',
        '- Pilot radii and areas use EPSG:32642 projected map metres; geodesic distortion and true-bearing conversion remain production validation tasks.',
        '- International peak-catalogue completeness, landmark verification, optical distinguishability, scoring and production skyline validation remain outstanding.',
        '- Google Drive destination/quota and Python upload authentication are not configured. Pilot artifacts remain bounded local files; no cloud transfer or deletion of earlier-day inputs occurred.',
        '- Native synthetic prerequisites passed five cases; pilot unit tests and command history are documented in the agent log.','']
    if '100km30' in reports:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        figures=PROJECT/'report/pilot';figures.mkdir(parents=True,exist_ok=True)
        fine=reports['100km30']['cases']
        fig,axes=plt.subplots(len(fine),1,figsize=(11,2.5*len(fine)),squeeze=False)
        for ax,case in zip(axes[:,0],fine):
            data=json.loads((PROJECT/case['horizons']['0.05']['path']).read_text(encoding='utf-8'))
            ax.plot(data['azimuth_grid_north_degrees'],data['horizon_degrees'],color='#20666e',linewidth=.8)
            ax.axhline(0,color='grey',linewidth=.5);ax.set_xlim(0,360)
            ax.set_ylabel('Elevation angle (degrees)');ax.set_title(case['observer']['observer_id'],loc='left')
        axes[-1,0].set_xlabel('Projected grid-north azimuth (degrees); pilot diagnostic')
        fig.tight_layout();fig.savefig(figures/'horizons.png',dpi=150);plt.close(fig)
        lines+=['','## Diagnostic horizon profiles','','![Measured pilot horizons](../report/pilot/horizons.png)','']
    atomic_json(PROJECT/'data/processed/pilot_summary.json',summary)
    (PROJECT/'docs/pilot_results.md').write_text('\n'.join(lines),encoding='utf-8')
    return summary
