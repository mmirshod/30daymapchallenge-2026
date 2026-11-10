> Publication authorized, 2026-11-10: optional Russian website translation is complete; 15 browser checks and 7 focused tests passed. User authorized several thematic commits, push and verification of GitHub Pages. Existing main/docs publishing source is retained. Earlier no-publication notices are historical.

> Current checkpoint, 2026-11-10: G6 local PDF/PNG and interactive Pages export are complete. User-selectable weights and browser checks pass; no commit/push/deployment. See docs/g6_checkpoint.md (or g6_checkpoint.md from docs).

> Current update, 2026-11-10: Horizon-only MPS is complete for all 1,302 observers; 15 eligible summits, no unknown visibility. See docs/mps_checkpoint.md (or mps_checkpoint.md from docs). Earlier MPS-unavailable statements describe historical scope.

## 2026-11-10: G4 verified; G5 NPS ready

G4 completed all **1,302** summits, with zero permanent failures/resource breaches. G5 verified **6,510 artifact hashes** (1.05 GiB), identities, band/edge consistency and all ranking inputs. NPS rankings, Top 10, elevation bands, special winners and 18 named/500 sampled sensitivity scenarios are complete. Spearman elevation/NPS **0.329**; highest summit (4,395.5 m) is NPS position **729**. Baseline leader `node:1544318728` scores **74.715**, but nearby scores/weight sensitivity do not support a uniquely best real-world summit. Complete MPS remains missing due to non-lake registry gaps; lakes stay excluded. After a temporary resource stop and RAM recovery, **51 tests passed, no skips**, and actual figures/projection QA were generated. See [G5 results](g5_checkpoint.md) and [frozen method](g5_methodology.md). Publication builds are G6; no deployment/commit occurred.

## G4 running - 2026-11-10 14:01:36 UTC+05:00

The user approved a 1 GiB RAM reserve and full G4 after a successful three-worker test. Six-observer benchmark passed in 64.86s (1.55x sequential reference), with exact G3 terrain/peak/skyline agreement and no resource breaches. Full background job is running; snapshot 33/1,302 complete, 0 failed, requested/active workers 3/3. Per-summit checkpoints and the tested live 3->1->3 control preserve completed work. Benchmark-based estimate is 3.91 hours of processing; an initial execution gap/retries are logged separately. See [G4 operations and controls](g4_operations.md). Earlier statements that full production was unauthorized/not started are superseded; scoring, uploads and deployment remain outside this run.

## 2026-11-10: G3 completed; lakes excluded from ranking

User removed lakes from ranking and authorized the skipped G1 test plus full G3 below 4 GiB entry RAM. G1 integration passed; the full suite passed **45 tests, no skips**. All twelve sequential 100 km / 30 m G3 cases completed in **207.39 seconds** within the benchmark (208.06 seconds enclosing command). Median complete observer case **17.08 seconds**; median linear 1,302-observer estimate **6.18 hours**, excluding publication/retries. Process-tree sampled RSS peaked at **487.8 MiB**, available RAM remained >=**3.12 GiB**. All twelve hash-validated checkpoints were reused on restart. Of 288 LOS checks, 234 were non-grazing with **98.72% agreement**; this is a diagnostic target sample, not accuracy ground truth. **No lake visibility was sampled**; all 24 supplied lakes remain excluded source records. Two exact-boundary target samples remain unknown. Complete non-lake MPS readiness is still open; production remains disabled. See [G3 evidence, figures and timing table](g3_checkpoint.md).

## 2026-11-10: G2 terrain/peak data ready; landmark readiness partial

All 1,302 observer circles plus 60 m halo pass exact full-raster coverage checks. The snapshot-aligned international catalogue has 2,052 eligible >=1,800 m point targets, including all observer IDs and 69 absent from the existing Uzbekistan extract. All 44 supplied landmarks match their GPX sources (35 within scope), but full membership/coordinates and lake geometry remain unresolved, so MPS readiness stays false. Tests: 40 passed, 1 default-threshold G1 integration skip; no G2 tests skipped. See [G2 evidence](g2_checkpoint.md). No G3 or full-cohort analysis started.

## 2026-11-10: G1 accepted

All six native GDAL smoke cases passed through the isolated Windows worker, run `622f84d75cc449fdb9f52d9a7b0e4d9e`. Full suite: **28 passed, no skips**, 87 upstream warnings, 5.29 seconds pytest time, including actual Windows subprocess integration under the normal 4 GiB entry gate. The user authorized validation despite the earlier low-memory result; the smoke invocation used a logged 3 GiB entry override while retaining the 2 GiB runtime reserve, commit/disk protections and unchanged production configuration. Smoke entry RAM was 3.90 GiB; minimum sampled worker RAM was 3.89 GiB. Earlier blocked attempts remain historical evidence. G2/G3 and full-cohort execution have not started.

## 2026-11-10: G1 adapter implemented, native acceptance awaiting RAM

The reusable GDAL adapter and safeguards are implemented. Full tests: **27 passed, 1 skipped**; actual-GDAL tiny fixtures passed in-process, while the Windows subprocess test remains skipped on resource gates. The six-case `gdal-smoke` entry check recorded 0.66 GiB free RAM against the unchanged 4 GiB requirement and launched no GIS worker. See [G1 evidence and resume command](g1_checkpoint.md). Do not mark G1 fully accepted until native smoke/integration succeeds. No G2/G3 or production run started.

## 2026-11-10: GDAL production direction approved

The user chose GDAL for this exploratory project after reviewing the pilot tradeoff. The current [GDAL roadmap](gdal_pipeline_plan.md) supersedes earlier GRASS production requirements and the strict 99% LOS agreement blocker. Keep 30 m terrain, 100 km, 1,302 observers and sequential batches of ten. GDAL disagreement remains a reported limitation; mandatory data integrity and synthetic tests remain. Configuration now records the selected backend, but the production adapter is not yet implemented and full-cohort execution remains gated. No new analysis, downloads or deployment occurred during replanning.

# Implementation checkpoint

## Latest: terrain pilot completed — 2026-11-09

See [measured pilot results](pilot_results.md). Memory recovered above the existing gates; GRASS passed all five synthetic cases. Completed three 10 km/30 m cases, twelve 100 km/90 m cases, three 100 km/30 m cases, angular skyline convergence checks and an independent three-case GDAL cross-check. All observers ran sequentially. Six additional GLO-30 tiles were downloaded and verified; earlier-day sources were preserved.

The current laptop completed this terrain pilot safely: sampled native process-tree RSS peaked around 657 MiB and scratch around 6.53 GiB; full Python/native case RSS peaked around 690 MiB. New project data occupies about 0.54 GiB after transient cleanup. These are pilot observations, not guarantees for every summit or later pipeline stage.

The 90 m visible-area differences were +32.3%, +19.9% and -21.2% against matched 30 m cases, failing the provisional 10% tolerance. GRASS 30 m matched-cell non-grazing profile agreement was 100% in the sample; supplied-point non-grazing agreement was 99.3% overall. GRASS native wall times were 184–254 seconds at 30 m; scaling the median gives about 68 hours for native terrain calculations alone across 1,302 observers. GDAL was dramatically faster but did not meet the sampled LOS agreement target in all cases; production backend is unchanged.

Full production analysis is **not approved or started**. Next review must address backend accuracy/performance, the raster observer-position convention, catalogue/landmark completeness and final metric definitions. Google Drive folder/quota/Python authentication remain unconfigured; no Drive transfer occurred. The historical resource stop below is superseded for the current pilot session.

## Historical checkpoint — 2026-11-06

## Completed and verified

- Approved study scope is the existing **1,302 mapped summits >=1,800 m**. No expansion or additional elevation shortlist was applied.
- Installed a separate native Windows environment under repository-root `.bts/env`, using official prebuilt conda-forge packages and no administrator installer. The original `.venv` remains in place.
- Python 3.12.16; **GDAL 3.12.3 command line and `osgeo.gdal` verified**; all requested Python package imports checked successfully, including ReportLab, Typer, pytest and PyOsmium.
- GRASS 8.5.0 installed and version startup verified through the project wrapper. **Viewshed backend validation is not complete**; do not infer algorithm readiness from version output.
- Implemented configuration, Python CLI/launcher, stage event logs, source fingerprints, atomic artifacts, resource gates, local source staging, deterministic pilot selection and resumable DEM acquisition code.
- Staged all 1,302 observer records as GeoParquet after count, ID, geometry, boundary, scope and DEM-ground checks. Elevation range remains 1,800.9–4,395.5 m. Saved a 12-observer sample, four per elevation tercile.
- Generated source/acquisition manifests: no missing nominal cells at 50 km, six at 100 km, eleven at 150 km (120 m interpolation halo included). No new terrain or international peak dataset was downloaded.

## Verification evidence

The main test suite passed **12 tests**, with two upstream Rasterio/NumPy deprecation warnings. After the later commit-capacity/telemetry change, the targeted resource/atomic-write suite passed **3 tests** (two overlap the initial suite; one new test). The full suite has not been rerun after that later change because the laptop is under acute memory pressure. No scientific rankings or real summit benchmark results exist.

Ignored machine-readable artifacts: `data/processed/{environment,preparation,source_manifest,pilot_observers,acquisition_plan,resource_checkpoint}.json`, `data/processed/observers.parquet`, and stage JSONL/bootstrap logs in `logs/runs/`. These files are generated locally and are not embedded in the published website. Source/decision documentation and the exact package lock remain reviewable in the project.

## Windows failures and fixes

1. Default sandbox networking refused the initial metadata download; approved network access succeeded.
2. The first long-prefix installation failed because Windows long-path support is disabled. A short workspace prefix and pinned micromamba 2.5.0 flat cache allowed all 230 locked packages to install. The failed extraction cache was subsequently removed using a verified workspace path and extended Windows paths; no prior-day data was deleted.
3. `micromamba run` attempted a global AppData process directory. The launcher now invokes the isolated interpreter directly with explicit DLL paths and workspace temporary directories.
4. GRASS's distributed batch file clears `GRASS_CONFIG_DIR`. The wrapper uses the package's unmodified Python entrypoint and a workspace configuration directory.
5. GRASS first-run temporary-project startup failed before a mapset was initialized. Synthetic validation uses an explicitly named disposable project instead.
6. `g.proj.exe` exited with Windows missing-DLL code 0xC0000135. PE import inspection identified the expected OpenMP filename `libomp140.x86_64.dll`; installed LLVM supplies `libomp.dll`. The matching issue is documented in [OSGeo/grass#7615](https://github.com/OSGeo/grass/issues/7615). The wrapper provides a byte-identical, SHA-256-checked alias in `.bts/grass-compat/`, without changing system DLLs or package-owned files. This allowed execution to progress to project creation, but the complete synthetic suite did not pass before the resource failure below.
7. Windows subsequently raised **WinError 1455 (pagefile/virtual-memory exhaustion)** during process-tree sampling; another process-inspection attempt encountered WinError 8. Telemetry now records sampling failures instead of letting its thread die silently. Both physical RAM and Windows available commit capacity gate further native work.

## Current stop condition

Final lightweight checkpoint measured **195,727,360 bytes available physical RAM (0.18 GiB)** and **894,582,784 bytes available commit capacity (0.83 GiB)**. Commit limit was 48,453,435,392 bytes; free C: storage was 22,263,009,280 bytes (20.73 GiB). These are momentary measurements, not installed-runtime memory requirements.

Entry gates for native validation and the pilot are **4 GiB available physical RAM and 4 GiB available commit capacity**; runtime reserves are 2 GiB each, with 15 GiB free disk. Acquisition execution also enforces resource reserves. No large downloads, mosaics, real viewsheds or pilot runs were started. All native validation attempts have exited; targeted stop checks did not terminate unrelated applications. Remaining authorization is already recorded; an additional approval is not needed to resume setup/preparation/pilot once resources pass the gates.

## Next work when resources recover

1. Re-run `doctor` and the full tests, then `native-smoke`; retain actual failure output if the GRASS backend needs more correction.
2. Validate availability/license/release metadata for missing DEMs and matching-date international OSM extracts; execute checked acquisition within the disk budget. Validate the landmark registry separately.
3. Prepare complete terrain/targets and run the bounded pilot. Review measured accuracy, resolution and full-run budget before production analysis. Commits, pushes and deployment remain unauthorized.

Use `tools/run.py` commands documented in the project README. No system settings or administrator action is part of this checkpoint.
