# G3: end-to-end GDAL benchmark

2026-11-10, Asia/Tashkent. **All 12 saved observers completed at 100 km / 30 m, sequentially.** Lakes are excluded from ranking and were not sampled for visibility. No full-cohort analysis or ranking was started.

## Measured execution

Original invocation: **207.39 seconds** inside the benchmark, 208.06 seconds for its enclosing logged command. Cases include window validation/preparation, isolated GDAL execution, exact-radius masking, terrain/distance/direction summaries, peak edges, 0.1-degree signed skyline extraction, non-lake landmark point diagnostics and independent LOS checks.

| Observer | GDAL core/output (s) | End-to-end case (s) | Visible terrain (km2) | Visible peak ground proxies | Non-grazing LOS agreement |
|---|---:|---:|---:|---:|---:|
| node:1544318396 | 1.30 | 18.02 | 75.99 | 28 | 100.0% |
| node:349032500 | 1.19 | 17.19 | 7424.06 | 159 | 100.0% |
| node:2575646105 | 1.20 | 17.97 | 308.53 | 24 | 100.0% |
| node:2540944031 | 1.31 | 18.08 | 57.97 | 52 | 100.0% |
| node:2594726988 | 1.05 | 16.70 | 39.90 | 52 | 95.7% |
| node:349033409 | 1.36 | 16.83 | 4527.94 | 308 | 100.0% |
| node:1544317630 | 1.09 | 16.47 | 2406.23 | 233 | 100.0% |
| node:2506952345 | 1.08 | 16.97 | 457.77 | 185 | 100.0% |
| node:2533272142 | 1.19 | 16.70 | 4589.65 | 56 | 93.3% |
| node:2593669682 | 1.03 | 15.19 | 2035.42 | 21 | 100.0% |
| node:2556670536 | 1.09 | 17.53 | 696.97 | 173 | 94.7% |
| node:349007556 | 1.09 | 19.58 | 514.53 | 316 | 100.0% |

Median stage times: GDAL core **1.14s**, complete GDAL adapter **11.25s**, terrain summary **2.78s**, target summary **0.13s**, skyline/LOS **2.87s**. Adapter costs include startup, terrain validation, compressed scratch writing, exact mask and provenance hashes; the 0.8-second independent pilot was not an end-to-end timing.

![Measured stages](../report/g3/stage_timings.png)

## Cost and resource interpretation

Median measured case: **17.08s**. Linear scaling to 1,302 observers gives **6.18 hours**, with a sampled min/max scaling span of **5.49-7.08 hours**. This is an estimate, not a confidence interval or promised runtime. It includes the benchmark's target/skyline/LOS work, but excludes publication, additional analyses, retries, sleep/breaks and initial cohort loading. Faster scratch/window preparation is a possible next optimization, not an already measured improvement.

Sampled command process-tree RSS peaked at **487.8 MiB**; minimum available physical RAM was **3.12 GiB**. Native resource safeguards stayed active. Per-invocation RAM entry was 2 GiB as explicitly authorized; production defaults remain 4 GiB. The 2 GiB runtime RAM/commit and 15 GiB disk reserves were preserved. Process RSS sampling may count shared pages more than once and can miss very brief peaks.

## Output interpretation and limitations

Terrain area uses projected cell area and a 100 km projected cell-centre mask. Peaks are zero-target-height GDAL raster-ground proxies sampled at catalogue coordinates; surveyed summit heights are not silently substituted. Self edges are excluded. Edge tables preserve model distances, geodesic distances, true bearings and unknown mask-boundary cases.

There are 2 unknown target observations at the exact raster mask boundary; they remain unknown rather than being converted to hidden. No terrain cells inside the mask are unknown. Stored G3 case artifacts total 10.7 MiB (plus checkpoint metadata). Maximum sampled native scratch was 160.0 MiB, including the shared monitored workspace temporary tree.

Skyline rays use the effective observer cell, half-cell radial spacing, curvature coefficient 1-k and WGS84 semimajor radius. Negative horizons remain valid. Each limiting point has projected coordinates and a geodesic bearing. Local angular contrast uses a provisional 0.5-degree circular smoothing / +/-5-degree minimum baseline; it is not topographic prominence or a finalized normalized ranking score.

![Signed skyline profiles](../report/g3/horizons.png)

Independent LOS checks: **288 total**, **234 non-grazing**, non-grazing agreement **98.72%**. Targets were selected deterministically across GDAL class/distance strata and supplemented to 24 rays per observer. This same-DSM target sample is not unbiased accuracy or ground truth, and does not erase the earlier GDAL/GRASS discrepancies from different terrain samples. Grazing checks remain separate and retained.

All 24 supplied lake waypoints remain in source audit files for provenance, with explicit ranking exclusion. Lake polygons and lake visibility are no longer required. Non-lake landmark diagnostics are unverified point proxies only; remaining official membership/missing-coordinate/visual-eligibility gaps still prevent a complete MPS. No NPS or MPS score was invented.

## Checkpoints and validation

Every observer has atomic metrics/checkpoint JSON, a GDAL raster/manifest, sparse Parquet peak edges, skyline JSON and independent LOS JSON under `data/interim/g3/19e4886a49c2821b/`. Checkpoints bind inputs, config, environment, algorithms and artifact hashes. Completed outputs are reused only after validation; stale/interrupted/corrupt checkpoints are rejected.

Current replay: 12 of 12 validated case checkpoints reused; invocation 0.08s. Original measured costs remain saved separately in `data/processed/g3_benchmark_measured.json`; replay costs do not replace fresh-run scaling evidence. Restart/failure/stale/corrupt artifact behavior and reserves have automated tests. Prior G1 integration passed with the explicit lower-entry override, and the pre-benchmark full suite passed 45 tests with no skips.

CSV timings: `report/g3/observer_timings.csv`. Machine summaries: `data/processed/g3_benchmark_measured.json` and `data/processed/g3_benchmark.json`. This checkpoint does not authorize 1,302-observer production, commits, Drive uploads or deployment.
