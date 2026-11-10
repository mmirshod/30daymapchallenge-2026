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

# Validation record

## 2026-11-09 terrain-pilot verification

- Full automated suite: 16 passed before final report/engine-summary additions; warnings came from upstream Rasterio/Affine/NumPy deprecations. Final verification is recorded in the agent log.
- Native GRASS synthetic checks: five passed. Initial restart collided with an old diagnostic output; per-run directories prevent that collision without overwriting earlier diagnostic files.
- Three local 10 km cases completed, including 216 diagnostic rays. Twelve 100 km/90 m cases completed, including 815 rays. Three 100 km/30 m cases completed, including 192 supplied-point rays plus separate cell-reference rays. All circle/halo coverage checks passed before those computations.
- At 30 m: supplied-point non-grazing LOS agreement 99.3% overall; matched-cell non-grazing agreement 100%. These are same-DEM, model-consistency checks, not survey validation. Raster observer-position effects remain documented.
- Median absolute visible-area change between 90 m and 30 m: 21.2%; provisional <=10% gate failed. No ranking-stability claim from three pairs.
- Three signed-horizon profiles compared 0.25°, 0.1° and 0.05° sampling. Preserve negative angles. Measured convergence statistics are in the pilot report; azimuth convention/prominence are not production-validated.
- GDAL cross-check: three cases completed rapidly, but matched-cell non-grazing profile agreement ranged 85.2–98.2%, below the proposed 99% acceptance target. Visible-pixel IoU with GRASS was 92.6–96.8%. Do not approve an engine based on speed or whole-circle pixel agreement alone.
- Full catalogue/landmark readiness and production approval remain false. No commits, pushes or deployment.

## Historical verification

2026-11-06, Asia/Tashkent.

| Check | Result |
|---|---|
| Explicit prebuilt environment installation | Passed: 230 package records installed; bootstrap exit 0. |
| GDAL executable and Python binding | Passed: both report GDAL 3.12.3. |
| Required Python imports | Passed in isolated environment; versions in generated environment manifest. |
| GRASS version startup | Passed through workspace wrapper: 8.5.0. |
| GRASS viewshed synthetic suite | **Not passed/completed.** Startup/packaging corrections were applied, then Windows virtual-memory exhaustion prevented reliable completion. No backend acceptance claim. |
| Core tests | 12 passed; two upstream deprecation warnings. |
| Follow-up resource/atomic-write tests | 3 passed after Windows commit-capacity gate was added. Full suite still needs a rerun after those changes. |
| Existing candidate staging | Passed: 1,302 distinct IDs/points, >=1,800 m, region membership within 1 cm numerical tolerance, valid sampled DEM ground. |
| Pilot sample and missing-tile manifests | Generated; these are preparation artifacts, not research results. |
| Full cross-border terrain / catalogue / landmarks | Incomplete; no readiness claim. |
| Real-terrain pilot and rankings | Not run. |

The initial pytest run had five temporary-directory fixture errors and seven passing tests; a corrected workspace temporary directory and sandbox execution context produced the later 12-test pass. Earlier failures remain part of the development record. A memory-sampler thread also failed under WinError 1455; its telemetry is incomplete and must not be presented as a measured peak for that entire native attempt.

Current resource measurements and exact blockers are in [status.md](status.md). Machine event logs are kept outside the published site. User-provided source files remain immutable inputs.
