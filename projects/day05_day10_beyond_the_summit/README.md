> Publication authorized, 2026-11-10: optional Russian website translation is complete; 15 browser checks and 7 focused tests passed. User authorized several thematic commits, push and verification of GitHub Pages. Existing main/docs publishing source is retained. Earlier no-publication notices are historical.

> Current checkpoint, 2026-11-10: G6 local PDF/PNG and interactive Pages export are complete. User-selectable weights and browser checks pass; no commit/push/deployment. See docs/g6_checkpoint.md (or g6_checkpoint.md from docs).

> Current update, 2026-11-10: Horizon-only MPS is complete for all 1,302 observers; 15 eligible summits, no unknown visibility. See docs/mps_checkpoint.md (or mps_checkpoint.md from docs). Earlier MPS-unavailable statements describe historical scope.

# G5 natural rankings are ready

[G5 results, Top 10 and sensitivity](docs/g5_checkpoint.md) and [frozen scoring method](docs/g5_methodology.md). G4 completed all 1,302 summits and all 6,510 artifact hashes passed verification. CLI: `tools/run.py rank`, then `tools/run.py ranking-report`. Full CSV/Parquet outputs are under `data/processed/g5/`; real figures are under `report/g5/`. Complete MPS remains unavailable, lakes excluded. Final tests: 51 passed, no skips. G6 reports/site and any deployment remain later work. Earlier running-job snapshots below are historical.

# G4 is running

Current operation: [three-worker benchmark, live progress and controls](docs/g4_operations.md). Each completed summit has a hash-validated checkpoint. Use `tools/run.py analysis-control 1` to reduce workers, `analysis-control 3` to restore, `analysis-control 0` to drain/pause, and `analysis-status` to read progress. The user approved a 1 GiB RAM reserve and full G4 after the successful benchmark. Earlier production-gate statements below are historical; rankings and publication remain later stages.

# Beyond the Summit

Day 05 Sight + Day 10 Prompting Only. Study population: the existing **1,302 mapped Tashkent summits >=1,800 m**, as approved on 2026-11-06. Conclusions are restricted to this cohort. Earlier-day sources and the root Python environment remain untouched.

Current G3 checkpoint: [measured end-to-end results](docs/g3_checkpoint.md). All twelve cases completed and restarted from verified checkpoints. Lakes are excluded from ranking. Median full-cohort estimate is 6.18 hours before reporting/retries; full production remains disabled. CLI: `tools/run.py g3-benchmark --entry-available-ram-gib 2`, then `tools/run.py g3-report`.

G2 checkpoint: [data-readiness evidence](docs/g2_checkpoint.md). Terrain/peak inputs are ready for G3; complete MPS is not. Re-run with `tools/run.py data-readiness --stage all --entry-available-ram-gib 2`; runtime safeguards remain active.

G1 checkpoint: [adapter implementation and acceptance evidence](docs/g1_checkpoint.md). Selected production backend is GDAL; all six native acceptance cases and 28 regression tests now pass. The full run remains disabled.

Historical pilot checkpoint: [status](docs/status.md) and [measured terrain pilot results](docs/pilot_results.md). GRASS synthetic validation and the bounded sequential terrain pilot now pass the resource gates; resolution/backend scientific findings still require review before production. Native work requires physical RAM and available commit capacity each above 4 GiB at entry.

## No-admin runtime

`tools/bootstrap.py` downloads checksum-verified micromamba 2.5.0 into repository-root `.bts/`. The short prefix and this release's flat package cache avoid Windows path limits when `LongPathsEnabled=0`; no registry modification is required. It performs a dependency dry-run by default. The reviewed `environment-win-64.lock.txt` lists explicit prebuilt conda-forge packages; `--install` recreates the environment from this lock without a source build or another solve. No shell initialization, global PATH or administrator installer is used. Metadata from the original attempted `.runtime/` bootstrap is retained; its invalid extraction cache was removed.

From the repository root, use the original interpreter for bootstrap only:

```powershell
.\.venv\Scripts\python.exe projects\day05_day10_beyond_the_summit\tools\bootstrap.py --install
```

The Python launcher below invokes the isolated environment and installs no project package into earlier-day environments:

```powershell
.\.venv\Scripts\python.exe projects\day05_day10_beyond_the_summit\tools\run.py doctor
.\.venv\Scripts\python.exe projects\day05_day10_beyond_the_summit\tools\run.py prepare
.\.venv\Scripts\python.exe projects\day05_day10_beyond_the_summit\tools\run.py gdal-smoke
.\.venv\Scripts\python.exe projects\day05_day10_beyond_the_summit\tools\run.py validate
```

The approved scenario is now **100 km only**, one observer at a time. For measured stages, the CLI also provides `pilot --phase local`, `prepare-pilot-dem --resolution 90`, `pilot --phase 100km`, `prepare-pilot-dem --resolution 30`, `pilot --phase 100km30`, `pilot-gdal`, and `pilot-report`. The 10 km phase is a startup benchmark, not a second research radius. Checkpoints validate source/config/algorithm fingerprints and output hashes before reuse; failed outputs and mismatches cannot be mistaken for completed work. Skyline pilot azimuths are grid-north diagnostics, not finalized prominence metrics.

`acquire` writes a missing-DEM acquisition plan; `acquire --execute` performs checked downloads only after resource checks. `pilot` requires at least 4 GiB available RAM and complete required inputs. `analyze` is blocked pending pilot/budget review. Scoring/report/site commands will be added as their stages are implemented; no placeholders generate invented outputs. `all` advances implemented local validation stages and stops at the first unmet pilot gate; it does not acquire data or publish.

Outputs and machine logs remain under ignored project data/log folders, outside the published `/docs` tree. Human decisions and actual prompt excerpts are in project `docs/`. Never commit, push or deploy without separate authorization.

