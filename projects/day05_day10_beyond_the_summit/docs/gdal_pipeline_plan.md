# Current checkpoint - G5 NPS complete, 2026-11-10

G4 completed all 1,302 observers and G5 verified 6,510 product hashes plus schema/count consistency. Natural rankings, elevation bands, special categories, descriptive elevation correlation and named/500-draw weight/skyline sensitivity are complete. Complete MPS remains unavailable due to unresolved non-lake registry evidence; lakes are excluded. Frozen exploratory method/config and results are in the project docs/g5_methodology.md and docs/g5_checkpoint.md. Tests:51 passed, no skips after RAM recovery. The next checkpoint is G6 publication builds when requested; no commit or deployment is authorized. Earlier running/gating statements below are historical.

# G4 authorization update - 2026-11-10

The user approved a 1 GiB RAM reserve, a three-worker benchmark and automatic full G4 after success. Benchmark passed: six cases in64.86s,1.55x sequential reference, all compared terrain/peak/skyline results identical. Full G4 is now running with per-summit checkpoints and tested live concurrency reduction. The benchmark-based full processing estimate is3.91hours before pauses/retries/publication. Three workers are the current maximum; 0 drains/pauses,1/2/3 select concurrency without invalidating work. Physical RAM reserve1GiB, Windows commit reserve2GiB and disk reserve15GiB. The prior sequential-only policy and production-not-approved gate below are superseded. Lake exclusion and unresolved non-lake MPS readiness remain in effect. Rankings and deployment are not part of this authorization.

# Beyond the Summit: GDAL implementation plan

Updated 2026-11-10 (Asia/Tashkent). This is the current roadmap and supersedes earlier GRASS production requirements. The user selected GDAL for this recreational, exploratory project after reviewing the measured speed/accuracy tradeoff. This authorizes replanning and backend selection; a full-cohort production run has not been started or approved by this request.

## Scope and assumptions

Evaluate all 1,302 existing mapped observation summits >=1,800 m, at 100 km only, using the prepared 30 m Copernicus terrain. Keep one worker and resumable batches of ten. Python orchestrates acquisition, GDAL, metrics, PDF generation and static website building. Preserve Days 01-04 unchanged. No manual QGIS/Figma steps, commits or deployment.

Use GDAL ViewshedGenerate, GVM_Edge, observer 1.7 m above DEM ground, terrain target zero, curvature coefficient 1-k = 0.85714 for k = 0.14286. Use EPSG:32642 for the raster engine; report geodesic distances/bearings and document projected radius/area distortion. Keep the 100 km output mask and interpolation halo. Do not replace missing terrain with zero. The 90 m experiment failed the area tolerance and is not the production baseline.

GDAL's output represents approximate terrain visibility from a raster cell, not verified real-world sight. Original summit coordinates remain in the records; record the effective observer cell and its ground height. Copernicus is a surface model and does not resolve every narrow ridge or summit. No claim of optical visibility through haze or clouds.

## Evidence and revised quality policy

The three 30 m GDAL cases took 0.83-0.91 seconds for compute/initial output, compared with GRASS viewshed times of 180-250 seconds. Aggregate core speedup was about 238x. Visible-pixel intersection over union was 92.58-96.78%; this is overlap, not recall. Independent cell-reference non-grazing LOS agreement was 85.19-98.21%. Preserve these results in the report; do not relabel GDAL as scientifically equivalent to GRASS.

For this exploratory project, the prior >=99% independent non-grazing LOS gate becomes a diagnostic rather than a production blocker. Deterministic synthetic correctness, complete terrain support, correct units/height/curvature, valid outputs, resource protection and reproducible checkpoints remain mandatory. Report sampled disagreements and near-grazing ambiguity; do not describe an untested peak or landmark as independently confirmed. Keep GRASS installed as an optional reference, with no GRASS requirement for each production observer.

## Implementation checkpoints

| Checkpoint | Work and tests | Reviewable output / exit condition |
|---|---|---|
| G1: production adapter | Extract reusable GDAL wrapper from the pilot; explicit settings, per-observer subprocess isolation, timeout/progress/resource monitoring, exact mask, atomic outputs and engine/input/config fingerprints. Test flat ground, blocking ridge, increased observer height, curvature and NoData rejection. | Versioned adapter, meaningful synthetic tests; production command still gated. |
| G2: data readiness | Check full-cohort 100 km plus halo coverage blockwise, not just the pilot sample. Acquire only missing terrain if needed. Acquire reproducible international OSM target peaks using bounded Python processing; stable IDs, deduplication, names, source heights and DEM ground provenance. Validate and deduplicate available program landmarks. | Coverage/source/license manifests, target/landmark tables and explicit gaps. Never fabricate missing heights or memberships. |
| G3: end-to-end batch | Run the saved 12-observer sample sequentially through GDAL, summaries, target sampling and skyline extraction. Reuse existing GRASS references; no expensive GRASS rerun required. Test restart, interrupted output, failed observer, stale fingerprints and reserves. | Actual end-to-end wall time, sampled RSS/scratch/output bytes, per-stage costs, LOS diagnostics and revised whole-cohort budget. Full run awaits budget/readiness review. |
| G4: cohort analysis | After approval, process all eligible observers in resumable batches of ten. Immediately reduce viewsheds to terrain area/distance bands/direction summaries and target visibility edges; discard only reproducible new scratch after successful checkpoint validation. | Per-observer metrics and coverage flags, sparse partitioned Parquet edges, horizon profiles and batch manifest; progress and failures reconciled to 1,302 IDs. |
| G5: ranking | Freeze documented component definitions and normalization; calculate NPS and separately eligible MPS, elevation relationship and weight sensitivity. Check ranks deterministically, missingness, bounds and denominator handling. | Full rankings, Top 10, elevation bands, raw/normalized metrics, limitations and sensitivity results. Missing metrics never become a fabricated complete score. |
| G6: publication builds | Python generates the three-page landscape Day 05 PDF plus page PNGs, separate three-page Day 10 process PDF, charts/CSVs and a locally staged static explorer. Test links, attribution, browser rendering and absence of raw/private data. | Reviewable local PDFs, figures and website. Publication needs separate authorization. |

## Metrics and practical simplifications

Terrain: compute area and visible fraction within 0-20, 20-50 and 50-100 km, plus open-direction coverage, blockwise. Sample target peaks from the same GDAL viewshed to avoid per-target engine launches; explicitly identify this as a raster-ground visibility proxy. A catalogued summit height above its DEM cell must not silently be used with the zero-target-height raster. Add targeted LOS checks if elevated-target geometry is introduced.

Skyline: retain independent Python radial horizon extraction. Start at 0.1 degree spacing, half-cell radial steps and chunked direction processing, guided by the completed pilot; record signed horizons, limiting terrain points and true-north conversion. Derive local angular prominence with documented smoothing/neighbourhood parameters; never call it conventional topographic prominence. Skyline cost may now dominate the fast GDAL stage. Prefer adaptive refinement of important features over an unbenchmarked 0.05 degree full-cohort run.

Keep provisional NPS weights terrain 30%, peaks 25%, skyline 30%, distance 15%; MPS 80% NPS + 20% verified landmark score. Freeze component definitions and compare plausible weight variants before publishing. Lakes/Mirage are excluded by user decision; lake polygons and visibility are not required and must not contribute to the score or its missingness penalty. Incomplete remaining landmark registries must be disclosed; publish partial landmark observations separately and defer complete MPS if necessary. No invented complete mountaineering ranking. Keep optional weather analysis out of the core build.

The 100 km restriction applies to scored peak/landmark visibility too. Distant program objects can be listed as outside scope without acquiring long corridors. This supersedes the original long-distance landmark extension.

## Runtime and storage budget

Core GDAL timing extrapolates to approximately 18-20 minutes for 1,302 observers. This excludes cropping, alignment, I/O, coverage checks, skyline profiles, target metrics, reporting and retries; it is not a promised full runtime. Measure G3 before estimating the total. GPU is unnecessary. Retain entry reserves of 4 GiB available RAM/commit and runtime reserves of 2 GiB, 15 GiB free disk, one worker, GDAL cache 128 MiB and bounded per-case scratch. Do not relax safeguards based on a three-observer benchmark.

Use one read-only shared terrain mosaic, one active observer window and compact persisted summaries. Production GDAL scratch should avoid GRASS mapset duplication; actual G3 high-water measurements determine the disk budget. Retain full viewshed rasters for selected examples and diagnostics, and make other rasters reproducible rather than retaining all 1,302 by default. This is a planned retention policy, not authorization to delete existing pilot or prior-day files.

Archive completed, verified batch artifacts to Google Drive when a destination, quota and Python API authentication are configured. Connector access does not automatically provide Python credentials. Keep active DEM/scratch local. Verify remote size/checksum and manifest before removing any authorized reproducible local copy. Unconfigured Drive does not block the small local integration benchmark, but local disk limits must gate production.

## Day 10 development record

Preserve exact user prompts with hashes, append decisions/interventions with dates, and record actual stage start/end times, code/config/input fingerprints, versions, resource samples, retries and validation outcomes in JSONL. Log the GDAL choice as a human-approved speed/accuracy tradeoff, including the three-case comparison and unresolved mismatches. Separate measured execution time from extrapolation and unavailable chat/model statistics. Python builds figures and the process report from these records; do not reconstruct unobserved agent effort or claim complete autonomy.

## Next step and remaining decisions

G1 is accepted and its skipped integration test has now passed. G2 terrain/point targets pass; lakes are explicitly excluded from ranking. G3 completed all twelve cases, with validated restart and a measured median scaling estimate of 6.18 hours for 1,302 observers before publication/retries. Full non-lake MPS readiness remains open. The next checkpoint is G4 after review of the measured full-run budget and remaining readiness gaps. The selected backend is now GDAL; no further backend permission is needed. Full-cohort execution remains gated on the integration budget/readiness checkpoint. Drive destination/authentication and handling of incomplete landmark membership remain unresolved. No commit, push or deployment is authorized.
