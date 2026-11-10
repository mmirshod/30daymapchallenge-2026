## 2026-11-10: G1 accepted

All six native GDAL smoke cases passed through the isolated Windows worker, run `622f84d75cc449fdb9f52d9a7b0e4d9e`. Full suite: **28 passed, no skips**, 87 upstream warnings, 5.29 seconds pytest time, including actual Windows subprocess integration under the normal 4 GiB entry gate. The user authorized validation despite the earlier low-memory result; the smoke invocation used a logged 3 GiB entry override while retaining the 2 GiB runtime reserve, commit/disk protections and unchanged production configuration. Smoke entry RAM was 3.90 GiB; minimum sampled worker RAM was 3.89 GiB. Earlier blocked attempts remain historical evidence. G2/G3 and full-cohort execution have not started.

# G1: reusable GDAL viewshed adapter

Checkpoint date: 2026-11-10, Asia/Tashkent. **Implementation and tiny-fixture tests complete; native Windows subprocess acceptance pending available RAM.** Production remains disabled. No real summit batch, acquisition, commit or deployment was performed.

## Delivered

- `src/beyond_the_summit/gdal_viewshed.py`: reusable `generate_viewshed` and immutable `ViewshedSettings`. Explicit GVM_Edge, zero terrain-target height, 1.7 m observer, curvature coefficient 1-k, 100 km maximum, 128 MiB cache default. Output restricted to this new project or workspace test temporary files; input replacement rejected.
- `gdal_worker.py`: one process per observer, blockwise support validation/cropping, projected metre CRS, north-up square cells, no unresolved NoData/nonfinite heights within circle plus two-cell halo, full halo bounds required. GDAL input elevations are assumed metres with source lineage still required; no vertical-datum transformation is implied.
- Output stays on the input grid without resampling, with values 0 hidden / 1 visible / 255 outside the exact supplied-coordinate projected-radius mask. Records effective observer cell/ground, curvature, versions, counts and timings.
- Unique per-case scratch, timeout, RAM/commit/disk reserves, scratch cap, own-process-tree termination, JSONL worker events and sampled native measurements. GDAL subprocess environment does not initialize GRASS or require its DLL compatibility alias. Runtime safeguards remain unchanged: 4 GiB entry RAM/commit, 2 GiB runtime reserves, 15 GiB disk reserve.
- Publish only the validated completed raster by atomic rename, followed by an atomic completion manifest. Manifest/signature covers DEM hash, coordinates/settings, config, environment lock, adapter/worker/resource-launcher code and GDAL version. Output hash is checked on resume. Failed replacement preserves the prior output/marker; stale or corrupted output cannot count as a valid checkpoint. Raster and manifest are separate atomic writes, with the manifest serving as completion marker.
- `gdal-smoke` CLI provides six actual subprocess acceptance cases and writes `data/processed/gdal_validation.json`; `validate` now inventories that evidence. Full-cohort `analyze` remains gated and unimplemented pending later checkpoints.

## Verification evidence

Full suite: **27 passed, 1 skipped**, 86 upstream deprecation warnings, 6.67 seconds pytest time. New test module contributes 11 passing tests plus one skipped integration test. Tiny terrain fixtures use the actual installed GDAL algorithm in the already-loaded test interpreter; only subprocess transport and OS resource gates are mocked for those fixtures. They are correctness tests, not native process/resource benchmarks.

Verified flat visibility, ridge occlusion, increased observer height, curvature on/off, exact circle mask, effective cell reference, checkpoint reuse, changed settings, corrupt-output repair, missing terrain / geographic CRS / incomplete halo rejection, preservation after failed replacement, invalid radius/input protection, timeout and disk/RAM/scratch stop paths. Safeguard tests use controlled resource snapshots and lightweight sleeping child processes; they never stop unrelated processes.

The first attempted test run was stopped by actual resource gates at approximately 0.43-0.45 GiB free RAM. The subsequent real `gdal-smoke` attempt recorded **0.66 GiB available RAM**, below the 4 GiB entry gate, and launched no GIS worker. Its machine-readable status is `blocked_or_failed`, passed=false, cases empty, run ID `68f5802d44464cc7989862ceb0f41863`. The separate-process pytest case was skipped on the same entry-resource condition. No resource limits were weakened in production code.

## Remaining G1 acceptance step

When at least 4 GiB RAM and available commit capacity are free, run from the repository root:

```powershell
.\.venv\Scripts\python.exe -u projects\day05_day10_beyond_the_summit\tools\run.py gdal-smoke
.\.venv\Scripts\python.exe -u projects\day05_day10_beyond_the_summit\tools\run.py test tests/test_gdal_viewshed.py -q
```

Require all six smoke cases to pass and the real subprocess test to run without a skip before marking G1 fully accepted. Existing authorization covers this bounded rerun; no new permission is needed. G2 data readiness and G3 end-to-end benchmarking have not started. The old independent GDAL pilot remains unchanged historical evidence, not proof that this new adapter passed native acceptance.

## Method limitations retained

This is exploratory raster-ground visibility, not verified real sight. The pilot's engine/LOS disagreements remain disclosed. Support is certified for circle/halo; missing data outside support is not filled with invented terrain. Supplied summit coordinates, effective raster cell, projected radius and vertical assumptions remain explicit. Target-peak elevations, skyline prominence, ranking and Drive archiving are later stages.

GDAL's official [viewshed documentation](https://gdal.org/en/stable/programs/gdal_viewshed.html) was checked for projected-CRS requirements, input-NoData limitations and curvature-coefficient conversion. It motivates explicit validation before the engine call.
