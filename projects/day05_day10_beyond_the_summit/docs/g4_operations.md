## Final status: G4 complete, 2026-11-10

All 1,302 observers completed, zero permanent failures and resource events. The scheduler has exited and final aggregate metrics exist. G5 subsequently verified all 6,510 output hashes and reconciled observer/edge/band tables. See [G5 results](g5_checkpoint.md). The running-job snapshots and controls below are retained as historical operating evidence.

# G4: three-worker benchmark and live analysis

Snapshot: 2026-11-10 14:01:36 UTC+05:00 (Asia/Tashkent). **Full G4 is running in the background**, not complete. Live counts are in `data/processed/g4_status.json` and will advance after this document was written. No ranking, commit, upload or deployment is implied.

## Authorization and resource policy

The user explicitly requested a 1 GiB RAM reserve, a three-worker test, and full G4 automatically after a successful test. The benchmark passed, so production analysis approval is now true in `config/analysis.yaml`. RAM runtime reserve is **1 GiB**; Windows commit reserve remains **2 GiB**, disk reserve **15 GiB**. The benchmark/live scheduler admits new workers only with additional RAM headroom, monitors available RAM/commit/disk and stops only its own work if actual reserves are breached. On a resource breach it reduces future concurrency to one. No unrelated application or system setting is changed.

Lake records remain excluded from ranking and visibility sampling. G4 computes natural terrain/peak/skyline metrics for all 1,302 approved >=1,800 m observers, plus explicitly unverified non-lake point diagnostics. Full MPS remains unresolved because of non-lake registry gaps. Scores remain null until G5; no complete MPS is fabricated.

## Three-worker benchmark

Six saved observers, two from each elevation tercile, ran in two waves with maximum active concurrency **3**:

- Parallel elapsed: **64.86 seconds**.
- Same-observer G3 sequential reference: **100.62 seconds**.
- Measured speedup: **1.55x**.
- Linear full-cohort estimate: **3.91 hours of processing**, before publication, inactivity and retries; not a promised completion time.
- Sampled process-tree RSS peak: **1.54 GiB**. Shared pages may be counted more than once.
- Minimum available RAM: **3.45 GiB**; no resource events, permanent failures or telemetry errors.
- All six terrain areas and visible-peak counts matched G3. A subsequent independent comparison confirmed all six 3,600-angle signed skyline arrays matched exactly (maximum difference zero).

The benchmark remains in `data/processed/g4_parallel_benchmark.json`, including source/model fingerprints and comparison checks. Its six complete observer products are reused in full G4.

## Current launch and progress

- Scheduler PID: `33268`; launcher PID: `21744`.
- Run ID: `ed0108b5e8654b148447445959529bc0`.
- Model signature: `8a7c7c8b46b04a2e3bb73d49a8b9ff5a9dceefdbda138c8f72e8b920683f7ab2`.
- At this snapshot: **33/1302 complete**, **0 failed**, requested workers **3**, active workers **3**.
- Hidden background Python launch output: `logs/analysis/g4_20261110_125734.stdout.log`; errors: corresponding `.stderr.log`.
- Machine launch record: `data/processed/g4_launch.json`.

There was a long execution gap after launch. Six initial attempts were retried; their recovered observer checkpoints completed successfully. The cause of that external gap was not established. Scheduler wall time includes the gap and must not be treated as uninterrupted compute time or used to replace the benchmark speed estimate. No failed summit was silently counted as complete.

## Live concurrency control

From repository root:

```powershell
# Reduce to one; active summit calculations finish first.
.\.venv\Scripts\python.exe projects\day05_day10_beyond_the_summit\tools\run.py analysis-control 1

# Restore three (or use 2).
.\.venv\Scripts\python.exe projects\day05_day10_beyond_the_summit\tools\run.py analysis-control 3

# Drain active tasks, then pause new scheduling.
.\.venv\Scripts\python.exe projects\day05_day10_beyond_the_summit\tools\run.py analysis-control 0

# Read progress without launching another analysis.
.\.venv\Scripts\python.exe projects\day05_day10_beyond_the_summit\tools\run.py analysis-status
```

The atomic live control file is `config/analysis_control.json`, polled by the scheduler. A reduction drains already active observers; it does not normally terminate valid work. Resource-driven termination is reserved for actual safeguard breaches. Runtime control, execution resources and approval flags are excluded from the numerical model key, so changing workers does not invalidate completed observers.

A real running-job control test reduced 3 to 1, observed **1 active worker** with **14 complete**, and restored three with the same model signature. Evidence: `data/processed/g4_control_test.json`. Automated scheduler tests also verify draining and restart reuse.

## Checkpoints, retries and outputs

Each summit has an isolated worker process and private output names; native GDAL opens its own datasets. Only the coordinator writes global progress. A completion marker is published last, after atomic raster/manifest, edge Parquet, horizon JSON and LOS JSON products and their hashes are verified.

- Checkpoints: `data/processed/g4/8a7c7c8b46b04a2e/cases/`.
- Products: `data/interim/g4/8a7c7c8b46b04a2e/`.
- Progress: `data/processed/g4_status.json` (every approximately two seconds).
- Per-observer requests/stdout/stderr: `logs/analysis/ed0108b5e8654b148447445959529bc0/`.
- Append-only actual execution events: `logs/runs/ed0108b5e8654b148447445959529bc0.jsonl` plus worker run logs.
- Final aggregate raw metrics: `data/processed/g4_observer_metrics.parquet`, compiled at scheduler completion. Ranking scores remain missing pending G5.

Resume with `tools/run.py analyze` if the scheduler exits. A per-model process lock prevents duplicate schedulers. Valid checkpoint hashes are scanned first; completed summits are skipped, and incomplete/corrupt/stale products are recomputed. Each pending observer has at most three attempts per invocation; unresolved failures remain explicit and can be retried on a later resume. A ten-minute observer watchdog handles stuck workers. Current checkpoints are finer than the planned ten-observer batch size, so reducing concurrency need not wait for a whole batch.

The active DEM and temporary rasters stay local. Compact production artifacts are expected to fit within the existing disk budget; the 15 GiB free-space safeguard remains authoritative. Google Drive destination/authentication is still unconfigured and no upload or verified archival is claimed.

## Validation

**47 tests passed, no skips** before launch, including live-control bounds, model-key stability, drain-on-reduction, checkpoint reuse, G1 integration and the previous terrain/peak/skyline/data tests. The real six-observer parallel benchmark passed and its products were checked against G3; the full live job control was also exercised. Original Day 01-04 files remain immutable. Full G4 is still running; do not interpret this checkpoint as completion of all analysis or publication outputs.
