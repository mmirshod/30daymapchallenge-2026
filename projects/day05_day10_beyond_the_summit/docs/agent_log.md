# Agent development log

## 2026-11-09 — Bounded terrain pilot

Actual start instruction is saved in `prompts/003_start_pilot.txt`. The preceding user-proposed 100 km-only/sequential/Drive archive scope is recorded in decisions D008–D010. Available physical RAM recovered to approximately 5.3 GiB at entry; no gate was lowered and no unrelated process was terminated.

The first default-sandbox pytest attempt encountered temporary-folder permissions; the authorized workspace-context retry passed 13 tests. GRASS's restart found a pre-existing synthetic output; switching to per-run diagnostic directories yielded five passing native cases. Added active subprocess resource/scratch/time monitoring and checkpointed pilot implementation. The initial three real-terrain 10 km cases completed in seconds; 215/216 supplied-point diagnostic profiles agreed, with the single mismatch within the explicitly labeled 2 m grazing band.

Acquired six missing GLO-30 tiles sequentially, with URL/remote identity/length/SHA-256 manifests, using the existing thirteen relevant tiles read-only. Derived 90 m and 30 m pilot mosaics from the same sources with bounded GDAL buffers. No source substitution to GLO-90 occurred. Prepared/executed twelve 100 km/90 m cases, then three 100 km/30 m cases, all sequential and checkpointed; validated complete circle/halo coverage and masked reported metrics at exactly 100 km. Smaller startup windows were excluded only for documented terrain gaps, preserving the sample's elevation terciles.

Added blockwise diagnostic sampling to avoid allocating several full coordinate grids for 30 m windows. Tests expanded to 16 passing cases, including alignment, missing terrain, sampling determinism and signed negative horizons. The first local run predated scratch telemetry; the report correctly marks its scratch peak unrecorded rather than zero.

Observed material DEM-resolution differences (absolute 19.9–32.3% in visible area), so 90 m was not accepted as the production baseline. Investigated point-versus-cell reference conventions using the upstream GRASS source; retained supplied coordinates and separate matched-cell diagnostics. GRASS's 30 m non-grazing agreement was 99.3% for supplied-point rays and 100% for cell-matched rays in these samples. Added three angular horizon convergence checks per fine-grid observer; profiles are grid-north pilot diagnostics and do not finalize skyline prominence or optical visibility.

GRASS 30 m viewsheds took 180–250 seconds, with approximately 657 MiB sampled native process-tree RSS and 6.53 GiB peak sampled scratch. A same-source GDAL cross-check was extremely fast (0.83–0.91 seconds compute/output), but had unresolved stratified LOS differences. Retained the GRASS production backend. Native-median extrapolation is approximately 68 hours across 1,302 observers, explicitly excluding skyline, peak/landmark work, retries and publication. This is a three-case extrapolation, not measured full execution.

Generated `docs/pilot_results.md`, machine summary JSON and a real diagnostic horizon PNG from the measured artifacts. No Drive destination/authentication is configured; pilot data remains local and bounded (~0.54 GiB after scratch cleanup). Production analysis, scoring, commits and deployment were not started.

Final verification: 16 tests passed (19 upstream deprecation warnings), protected Day 03/04 input fingerprints matched the initial audit, Python source syntax and document links passed, and pilot phase counts/aggregation gates were checked against actual artifacts. Final validation explicitly leaves full data readiness and production approval false. Remaining methodological limits include projected-versus-geodesic distances, true-north bearings, raster observer position and unvalidated production prominence/peak/landmark metrics.

## 2026-11-06 — Runtime setup begins

Actual user instruction is preserved in `prompts/002_implementation_authorization.txt`. The four root audit documents describe the earlier discovery; those are summaries, not full machine telemetry.

The agent rechecked resources: 1.33 GiB available RAM, about 33.92 GiB free disk. The user's >=1,800 m cohort restriction resolves the candidate-scope decision. Package installation is authorized without administrator rights. Official GRASS and GDAL documentation identify prebuilt Windows conda-forge distributions; project-local micromamba is selected. Environment bootstrap records timestamps, commands, exit codes and wall durations under ignored `logs/runs/` before data processing starts.

The initial sandbox download failed with connection refused; the authorized network retry downloaded and verified micromamba 2.10.0. A successful dry-run resolved 230 packages with approximately 465 MB total download size. The explicit package lock preserves the actual solver output.

The first installation failed during extraction at long Windows paths; the error and missing-cache-member messages are preserved in its JSON result. A separate memory snapshot during setup found approximately 90 MiB available. A targeted check intended to stop only this project's micromamba process found it had already exited; no unrelated process was terminated. The initial console update about stopping the installer preceded this observed outcome.

The agent verified disabled long-path support, selected official micromamba 2.5.0 and moved the runtime prefix to repository-root `.bts/`. This is a path/layout workaround, not a source build or registry edit. Bootstrap was extended to monitor future installer attempts and stop after sustained critically low memory; that extension was written while the retry was already running, so do not retroactively claim telemetry from the in-flight attempt.

Implemented local configuration, CLI, append-only stage logs, atomic JSON artifacts, resource gates, candidate staging, deterministic elevation-stratified sampling, tile acquisition planning, checked download resume, and tiny native smoke-test code. Added tests; execution outcomes will be recorded after the runtime becomes available. The original project overview attachment was preserved byte-for-byte as `prompts/001_project_overview.md`.

The short-prefix installation completed successfully with all 230 packages. `micromamba run` hit an AppData proc-directory permission error; direct interpreter invocation plus explicit DLL paths avoided it. The first pytest execution had temporary-directory fixture errors; the corrected workspace-only temporary path/execution context passed 12 tests, with two upstream warnings. A later targeted run passed three resource/atomic-write tests after the commit-capacity change.

GDAL CLI/Python bindings were verified at 3.12.3. GRASS version startup passed at 8.5.0 after bypassing the batch file's reset of `GRASS_CONFIG_DIR`. Native synthetic attempts exposed first-run mapset initialization and the missing OpenMP DLL alias documented in OSGeo/grass#7615. A project-only, hashed alias was added from the installed LLVM DLL. The complete native synthetic suite remains unvalidated: Windows subsequently exhausted virtual-memory/pagefile capacity (WinError 1455), and a process-inspection attempt also failed with WinError 8. Native attempts exited; targeted stop checks did not touch unrelated user processes.

Local candidate preparation completed successfully: 1,302 observer records staged, a 12-observer sample chosen, and radius-specific DEM manifests written. Acquisition planning identified eleven missing cells for the 150 km domain; acquisition execution was not started. No terrain downloads or real-summit visibility calculations were performed. The invalid first-install cache was removed; its metadata/logs remain. Final status, resource evidence, known limitations and resumption steps are documented in `status.md`, `validation.md` and `limitations.md`.


## 2026-11-10: GDAL replan

Updated backend selection and the implementation roadmap following the user decision. Planned a reusable GDAL adapter, mandatory synthetic/coverage checks, international target readiness, a 12-observer end-to-end budget checkpoint, compact batch storage and honest exploratory reporting. No pipeline execution or new data acquisition in this step.

## 2026-11-10: G1 implementation and validation

Implemented the selected GDAL adapter, isolated worker, validated mask/grid/provenance, checkpoint publication and native safeguards. First integration attempts stopped at actual low-RAM gates. Tiny real-GDAL fixtures then ran in-process with mocked process transport/resource gates; full suite 27 passed, 1 skipped (86 upstream warnings). Explicit gdal-smoke remained blocked at 0.66 GiB free against 4 GiB entry, with no GIS worker launched. Full G1 acceptance is pending; see g1_checkpoint.md. No downloads, production, commit or deployment.

## 2026-11-10: G1 native acceptance completed

User requested validation despite 3.76 GiB available RAM. Added an explicit per-invocation entry RAM override, bounded below by the unchanged runtime reserve and logged with the invocation. Production config remains 4 GiB. Ran gdal-smoke --entry-available-ram-gib 3: six native cases passed, entry RAM 3.90 GiB, minimum sampled worker available RAM 3.89 GiB. The subsequent full suite passed 28 tests with no skips (87 upstream warnings), including the default-threshold native integration case. G1 accepted; no production or G2/G3 work started.

## 2026-11-10: G2 data readiness

User authorized G2 below 4 GiB entry RAM. Implemented Python-driven blockwise exact support certification, filtered streaming PBF reconciliation, small historical Overpass acquisition with provenance, target catalogue QA and landmark/official roster audit. Initial query envelope was conservatively expanded; eligible counts remained 2,052. Two malformed/nonpoint peak objects were preserved but excluded under OSM point-mapping policy. Corrected raw Cyrillic program labels to canonical labels while retaining source labels. Final cached run 46ee84cfcba240fdbcbd79085ec2c910 took 14.92s; terrain/targets ready, MPS false. Final tests 40 passed, 1 existing default-gate integration skip. Protected input hashes unchanged. No G3, full cohort, commit, upload or deployment.

## 2026-11-10: lake exclusion, G1 rerun and G3

User excluded lakes and authorized G1/G3 below 4 GiB. Added explicit config/object exclusions and refreshed G2 artifacts; all 24 lakes retained only as excluded provenance. The previously skipped real G1 integration test passed with a process-local BTS_TEST_ENTRY_RAM_GIB=2 override; the full suite then passed 45 tests, no skips (114 upstream warnings). Production config remains 4 GiB and runtime reserve 2 GiB.

Implemented twelve-case end-to-end GDAL terrain/peak summaries, true-bearing signed skyline extraction, provisional local angular-contrast diagnostics, deterministic independent target LOS checks, non-lake point diagnostics, hashed atomic checkpoints and measured report generation. Fresh run 1afcfa5b355b4c0e821329b8b586d750: 207.391s benchmark, 208.063s command, median case17.078s, extrapolated6.1765h for 1,302 before publication/retries. Sampled RSS511,463,424B; minimum availableRAM3,345,084,416B; no telemetry errors. Saved original measured JSON before replay. Replay c3c52d26d776484d983288ccf3c17909 reused12/12 hashes; preserved original cost estimates.

288 independent target rays,234 non-grazing,231 agreeing non-grazing; not ground truth or an unbiased terrain sample. Two exact-mask target samples remain unknown. Generated and visually inspected real skyline/timing PNGs; adjusted timing legend to avoid covering bars. No lake points sampled. No full-cohort analysis, ranking, cloud upload, commit or deployment.

## 2026-11-10: three-worker gate and G4 launch

User authorized 1 GiB RAM reserve, test three workers, then automatically start full G4 after success, with adjustable concurrency/checkpoints. Implemented isolated per-summit workers, single coordinator, stable physical-model hashes excluding control/resources/approvals, per-summit atomic completion markers, bounded retries/watchdog, resource admission, own-process-only stops and live atomic 0/1/2/3 worker control. Full regression passed 47 tests, no skips.

Benchmark c5517396abaf47869fc7d91a2896bc0a: six observers, three maximum active, 64.86s vs 100.62s sequential reference, 1.55x speedup, 3.91h linear processing estimate; minimum free RAM 3.45GiB, sampled tree RSS 1.54GiB, no resource events. All areas/peak counts and signed skyline profiles matched G3 exactly. Set production approval true only after this passed, refreshed G2 hashes, and launched hidden background Python G4 (launcher21744, scheduler33268, runed0108b5e8654b148447445959529bc0). Reused six benchmark checkpoints.

Initial long execution gap led to six retry events; cause unverified, recovered without permanent failures. Confirmed actual live reduction 3->1 while work continued, then restored3; proof saved in g4_control_test.json. Snapshot 33/1,302 complete, 0 failed. Job continues beyond this response. No claim of full completion, no full MPS, no ranking/commit/upload/deployment.

## 2026-11-10: G4 verification and G5

User requested checking results and proceeding to G5. Confirmed scheduler complete,1,302/1,302, zero permanent failures/resource events; aggregate exists. Before inspecting winners, froze exploratory_g5_v1 weights/submetric normalization and documented method. Implemented complete artifact/source/model audit, multiscale circular angular signal prominence, bounded non-imputing cohort-percentile component scores, deterministic ranks, elevation-band/special categories, descriptive correlations,18 named sensitivity cases and500 reproducible weight draws. Verified6,510 hashes/1,128,137,219bytes in51.188s and reconciled aggregate/band/edge schemas.80 unknown peak observations retained across77 observers.

NPS leader node:1544318728=74.7152458, second74.6866359; Spearman0.3285758, Pearson0.3380382. Highest4395.5m observer position729. All1,302 MPS values remain missing. No method retuning after winners. Projection QA:2,045,825 edges, max absolute discrepancy34.53m, maximum geodesic target range100.02850km under100km projected mask.

Core ranking completed. Initial report/projection run and forced native repeat stopped below1GiB free RAM (0.59/0.52GiB);50 other tests passed. Asked user to free RAM while saving a lightweight summary. RAM recovered, user confirmed rechecking, observed4.15GiB free. Full figures/projection report completed; final suite51 passed/no skips/114 upstream warnings in8.38s. Visually inspected generated ranking and robustness PNGs. Publication/G6 and complete MPS remain outstanding; no commit/push/deployment or source-data change.


## 2026-11-10 ? MPS execution

User authorized MPS calculation after scope clarification. Codex matched fifteen GPX points to frozen OSM targets within one metre, reviewed official roster aliases, froze method, reused hash-checked G4 edges, calculated 1,302 MPS values and sensitivity variants. Three focused tests passed; old NPS files remain unchanged. One manifest type error fixed; one RAM-gated attempt stopped safely and rerun after recovery. See mps_checkpoint.md. All actions performed through code; no commit/deployment.


## 2026-11-10 ? G6 completed locally

Python generated two three-page landscape reports and six rendered PNGs, vendored Leaflet, exported all 1,302 summits with lazy details and built interactive weights, CSV and shared URLs. Actual Edge QA passed twelve scenarios; seven focused tests passed. A memory gate paused the first attempt; user freed RAM. PDF inspection led to coordinate-label and footer fixes. Existing docs/day05 contained only .gitkeep and was safely populated. Protected source hashes unchanged. See g6_checkpoint.md for actual measurements and review instructions; no external publication.


## 2026-11-10 ? Russian translation and publication authorization

Codex added an optional RU/EN presentation layer, including dynamic details, weights, filters and methodology. URL/browser persistence and bidirectional switching were verified without changing scores; Russian 390px layout has no horizontal overflow. Fifteen real Edge checks and seven focused tests passed. GitHub metadata confirms public repository main and existing built main/docs Pages source. User authorized several commits, push and deployment verification; no new permission question is required.
