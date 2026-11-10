# Scientific and technical decisions

## D001 — Candidate scope approved, 2026-11-06 (Asia/Tashkent)

The user states: “For the purpose of this project we consider only 1800+m peaks”. Retain the existing 1,302 candidates and the prior inclusive >=1,800 m selection. Report all conclusions as applying to this mapped cohort, not all regional summits. No additional elevation shortlist is allowed. Cross-border target peak completeness is a separate data concern.

## D002 — Implementation and package installation authorized, 2026-11-06

The user authorized proceeding according to the plan and installing additional packages, while explicitly stating that the laptop has no administrator access. All new runtime files must remain inside the project workspace; do not modify earlier-day environments, system PATH, profiles or registry. Use official prebuilt distributions rather than attempting a Windows source compilation of GDAL. The full-analysis gate after the pilot and the prohibition on unauthorized commits/deployment remain in force.

## D003 — Resource recheck

Immediately after authorization, psutil measured 1,427,275,776 bytes (1.33 GiB) available RAM, total 16,605,564,928 bytes. C: had 36,423,024,640 bytes free. This is an improvement over the initial audit but remains below the planned 4 GiB entry gate for a realistic pilot. Continue bounded environment setup and small validation work; recheck before larger work. Do not terminate unrelated user processes.

## D004 — Runtime distribution choice

Use micromamba as a project-local executable, with an isolated conda-forge environment containing Python 3.12, GRASS 8.5 and GDAL. This supplies precompiled native dependencies without an admin installer. Dry-run the solve, inspect download/installed sizes, then install if the disk budget fits. Verify the bootstrap archive against official package metadata and retain an explicit environment lock after installation.

Sources checked 2026-11-06: [GRASS conda availability](https://grass.osgeo.org/news/2026_05_27_grass_on_conda_forge/), [GDAL binary distributions](https://gdal.org/en/stable/download.html), [micromamba installation](https://mamba.readthedocs.io/en/stable/installation/micromamba-installation.html).

## D005 — Windows path-length workaround

The first full installation with micromamba 2.10.0 under the long project prefix failed with missing cache members and a `remove_all: directory is not empty` error. Registry inspection confirmed `LongPathsEnabled=0`. Switch to verified micromamba 2.5.0 (flat cache layout) and the short repository-root `.bts/` prefix. Keep the exact resolved 230-package environment; do not weaken dependency constraints or require admin rights. The first attempt's environment was incomplete and is not used.

During setup, measured available RAM fell as low as about 90 MiB. The agent issued a targeted termination check for its own installer; the installer had already exited with its extraction error before that check found a running matching process. No unrelated process was terminated. Setup was retried with the path workaround; the realistic pilot's 4 GiB RAM gate remains unchanged.

## D006 — GRASS wrapper and OpenMP alias

Preserve the installed distribution. Invoke its Python launcher with workspace-only configuration, bypassing the batch file's configuration reset. Use explicitly named disposable projects to avoid its first-run temporary-project check. PE dependency inspection identified an absent `libomp140.x86_64.dll`; provide a SHA-256-verified byte-identical alias of the already installed LLVM `libomp.dll` in `.bts/grass-compat/`, following the observed issue in [OSGeo/grass#7615](https://github.com/OSGeo/grass/issues/7615). Version startup passes; full synthetic visibility acceptance is still required. Do not call this a scientifically validated backend yet.

## D007 — Stop native work on insufficient Windows memory

Windows raised WinError 1455 during native validation and WinError 8 during process inspection. Require both >=4 GiB available physical RAM and >=4 GiB available commit capacity before native validation/pilot; keep >=2 GiB reserves during later processing. This extends the existing RAM gate to the actual Windows failure mode. Do not change system pagefile settings or terminate unrelated applications. Existing authorization covers resuming setup/preparation/pilot when resources pass; production and deployment gates are unchanged.

## D008 — Reduced scope and pilot authorization, 2026-11-09

The user proposed 100 km only, sequential batches and archiving to Google Drive, then instructed “let's start pilot”. Set maximum analysis radius to 100 km, remove 50/150 km sensitivity scenarios and 100+ km distance bands, keep one worker and a batch size of ten. Smaller 10 km windows remain allowed for the planned initial smoke benchmark; they are not an alternative research radius. Preserve >=1,800 m candidate scope.

At pilot entry, available physical RAM was 5,708,656,640 bytes and available Windows commit capacity 20,806,336,512 bytes, satisfying the existing gates. No resource thresholds were relaxed. Native subprocesses now enforce RAM/commit/disk reserves, timeouts, an 8 GiB sampled scratch cap and terminate only their own process trees on a failed gate.

Google Drive archive destination, quota and Python API authentication remain unconfigured. Keep the bounded pilot local; do not relocate prior-day data or delete local artifacts on the assumption of an unverified upload.

## D009 — Pilot coverage and raster conventions

Acquire the six missing 100 km GLO-30 tiles into this new project's raw directory; record URLs, retrieval time, remote identity, byte length and local SHA-256. Reuse thirteen earlier cache tiles read-only. Derive 90 m and 30 m EPSG:32642 mosaics from the same source, with bounded GDAL cache/warp buffers. Every computed circle plus a two-cell interpolation halo must contain valid terrain. NoData beyond that circle/halo may remain outside the computational support; it is not replaced by fabricated heights.

The native search radius includes one extra pixel so the exact 100 km centre-of-cell mask is covered despite raster indexing; metrics and target sampling remain capped at 100 km. Keep all supplied summit coordinates. Record independent point-reference LOS diagnostics separately from cell-centre diagnostics. The [GRASS source](https://github.com/OSGeo/grass/blob/main/raster/r.viewshed/main.cpp) documents cell-centre visibility; its curvature uses the current ellipsoid's semimajor axis. Cell-matched diagnostics use that convention, while point diagnostics retain the supplied coordinates. Neither is ground-truth surveying.

## D010 — Independent engine comparison

Benchmark GDAL ViewshedGenerate (GVM_Edge) on the same three 30 m terrain windows after the GRASS cases, with curvature coefficient 1-k, target height zero and explicit 100 km masking. This is a pilot cost/algorithm cross-check, not approval to replace the production GRASS backend. Retain algorithm disagreements and require review before any backend/resolution change.


## D011 - GDAL selected for exploratory production, 2026-11-10

User instruction: "considering dramatic speedup and that this is not real research project but more for fun right now, let's re plan the pipeline using GDAL". Select GDAL ViewshedGenerate GVM_Edge, keep 30 m / 100 km and sequential batches. Accept the measured engine disagreement as an explicitly disclosed exploratory limitation; do not claim equivalence or ground-truth accuracy. The old 99% sampled LOS gate becomes diagnostic. Require synthetic/data-integrity/resource checks and a 12-observer full-pipeline benchmark before a separately reviewed full-cohort run. Preserve GRASS pilot evidence. This request authorizes replanning, not a full run or publication. See gdal_pipeline_plan.md.

## D012 - Bounded G1 entry override, 2026-11-10

User instruction: "let's validate G1 anyway" after the RAM recheck. Permit an explicit logged 3 GiB entry RAM threshold for this tiny native acceptance invocation. Keep production defaults at 4 GiB and runtime RAM reserve at 2 GiB; reject overrides below that reserve. All six native acceptance cases passed. Full regression including normal-threshold subprocess integration also passed (28 tests, no skips). G1 is accepted without authorizing a full-cohort run.

## D013 - G2 lower entry threshold and thematic OSM acquisition, 2026-11-10

The user authorized G2 even below 4 GiB. Use an explicitly logged 2 GiB G2 entry floor, preserving runtime RAM/commit/disk reserves and production defaults. Replace planned large regional PBF acquisition with a small reproducible historical Overpass nwr query, snapshot-aligned to the existing local PBF; reconcile all local point nodes and source coordinates. Use point peaks >=1,800 m in any observer's 100 km radius, preserve subthreshold QA records, and exclude two nonpoint peak-tagged ways under the OSM point-mapping convention with their original evidence intact. A target's OSM height does not replace DEM ground in viewshed geometry. Landmark membership, missing program coordinates and lake geometry are unresolved; complete MPS remains gated while natural-panorama data is ready for G3. This does not authorize a full run or publication.

## D014 - Exclude lakes and authorize complete G3, 2026-11-10

The user instructed ignoring lake visibility in ranking and authorized the previously skipped G1 test plus full G3 below the 4 GiB threshold. Set landmarks.excluded_object_types=[lake], retain all source records with explicit exclusions and remove lake geometry from current requirements. MPS will not include Mirage/lake contributions or penalize their absence; future normalization must use only included, verified landmark types. Other non-lake registry gaps remain explicit.

Run G1 integration with a logged process-local test override, and G3 with a 2 GiB entry floor while retaining runtime RAM/commit/disk safeguards and unchanged production defaults. G3 uses the twelve saved stratified observers, one worker, 100 km / 30 m, 0.1 degree skyline steps and half-cell radial sampling. Match the GDAL effective observer cell for horizon/independent ray diagnostics and compute true bearings to limiting points. Provisional local angular contrast is not topographic prominence or a finalized score. G3 is complete; a full 1,302-observer run remains subject to its separate budget/readiness checkpoint.

## D015 - One GiB RAM reserve, three-worker gate and full G4 authorization, 2026-11-10

User instruction: retain only 1 GiB reserved, test first with three workers, then start full G4 after a successful test; preserve checkpoints so worker count can be reduced anytime. Apply the 1 GiB threshold to physical RAM while retaining 2 GiB Windows commit and 15 GiB disk reserves. The six-observer three-worker benchmark passed resource/correctness/speed checks, activating the user's conditional production authorization. Run all1,302 natural-metric observers in the background with per-summit checkpoints, a live 0/1/2/3 worker control and stable model signatures independent of execution concurrency. Reductions drain active summits; only resource breaches require own-worker termination/retry. Non-lake MPS gaps remain explicit and no scoring/deployment authorization is inferred.

## D016 - Exploratory G5 score freeze, 2026-11-10

User authorized G4 verification and G5. Freeze the existing30/25/30/15 NPS weights before scoring, with documented zero-anchored empirical mid-percentiles, directional fractions, multi-scale angular signal prominence/complexity and explicit distance/angular-relief proxies. Retain signed horizons and original height provenance. Deterministic ID ordering only resolves tied presentation; no rounded-score tie fitting. Compare18 named scenarios and500 seeded weight draws, including smoothing/nearfield ablations and unknown-count-only sensitivity. Correlations remain descriptive, not causal/iid hypothesis tests. Missing non-lake landmark evidence does not become an invented zero L or partial MPS; complete MPS remains missing. Figures/report were completed after memory recovered above the unchanged1GiB reserve. G6/publication has not been authorized by this request.


## D017 ? Horizon-only MPS, 2026-11-10

User excluded Cascade/Underground and supplied Snow Leopard nodes; all five checked outside 100 km. Missing 21st Horizon summit is outside scope per user. User requested MPS calculation. Freeze fifteen-landmark denominator, L count/distance/angular-relief weights 70/15/15, MPS 80/20; retain count-only and 10%/30% sensitivity. Results and identity reconciliation are in mps_checkpoint.md and mps_methodology.md.


## D018 ? G6 static export and interactive weights, 2026-11-10

User requested PDF + GitHub Pages export and selectable weights. Codex implemented normalized browser-only NPS weights and MPS landmark share, kept internal metrics fixed, generated two three-page PDFs and PNGs, and staged docs/day05 with a manual Pages workflow. Seven focused tests and twelve Edge scenarios passed. No commit, push or deployment was authorized/performed.


## D019 ? RU/EN and GitHub publication, 2026-11-10

User explicitly authorized optional Russian translation, several thematic commits, push and a verified Pages deployment. Preserve existing main/docs Pages source rather than changing it. Translation changes presentation only, retains language in URL/localStorage and preserves option values and all score/data identities. PDF reports remain English and are labelled EN in Russian UI. Fifteen Edge checks and seven focused export/MPS tests passed. Pre-existing untracked Day 03 DEM and temp.py remain local; runtime/raw data/caches stay ignored.
