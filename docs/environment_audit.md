# G3 measured update, 2026-11-10

All twelve sequential GDAL at 100 km / 30 m end-to-end cases completed in 207.39 s (208.06 s enclosing command); median 17.08 s per observer scales to about 6.18 hours for 1,302 before publication/retries. Sampled process-tree RSS peaked at 487.8 MiB; minimum available RAM 3.12 GiB. Maximum sampled native scratch was about 160 MiB; G3 retained artifacts total about 10.7 MiB. These bounded measurements supersede GRASS cost estimates for the chosen backend; they are not guarantees for all terrain/runs. User authorized a 2 GiB entry floor for G3; production defaults remain 4 GiB and runtime reserves 2 GiB. See [G3 report](../projects/day05_day10_beyond_the_summit/docs/g3_checkpoint.md). Historical audit follows.

# Beyond the Summit: environment audit

**2026-11-09 update:** recovered memory allowed the bounded sequential terrain pilot to complete. GRASS passed five synthetic cases, twelve 100 km/90 m cases and three 100 km/30 m cases. Sampled 30 m native process-tree RSS peaked around 657 MiB; scratch peaked around 6.53 GiB. The earlier memory-block measurements below are historical. See [pilot results](../projects/day05_day10_beyond_the_summit/docs/pilot_results.md) for measured cost and scientific gates. Production remains unapproved.

Audit date: **2026-11-06, Asia/Tashkent**. Discovery only; no packages installed, data downloaded, visibility benchmark run, pipeline implemented, commit created or deployment performed. Findings describe this session, not a guarantee of future runtime resources.

**Follow-up authorized 2026-11-06:** the user approved package installation and implementation without administrator rights. A subsequent resource check found 1.33 GiB available RAM, still below the 4 GiB pilot entry gate. Runtime setup and current evidence are recorded in `projects/day05_day10_beyond_the_summit/docs/`; the original findings below remain the discovery snapshot. Windows `LongPathsEnabled=0` was subsequently verified; use a short workspace runtime prefix rather than changing registry settings.

**Latest checkpoint:** the isolated environment installed successfully; standalone GDAL 3.12.3 and its Python bindings are verified. GRASS 8.5.0 starts, but its visibility validation remains incomplete after Windows virtual-memory exhaustion. The final lightweight check measured 0.18 GiB available physical RAM, 0.83 GiB available commit capacity and 20.73 GiB free disk. See [implementation status](../projects/day05_day10_beyond_the_summit/docs/status.md) for exact evidence and resumption requirements. Earlier package/resource tables are historical discovery measurements.

## Verdict

Python 3.12 and the existing vector/raster stack can read the relevant local data. The environment is **not ready for production visibility analysis**: no GRASS or standalone GDAL tools were found, several required Python packages are missing, and available RAM was only 1.13–1.19 GiB. Prefer a separate project environment and a native Windows GRASS subprocess backend, subject to installation approval and smoke tests. Do not assume Linux exists.

## Host and resources

| Item | Observed evidence |
|---|---|
| OS | Python reports Windows 11, x64, build 26200; registry DisplayVersion 25H2. Registry ProductName says Windows 10 Pro, a conflicting label; retain build/platform evidence rather than infer edition. |
| Shell | PowerShell; repository is on C:. |
| Processor | Intel Core Ultra 5 125U; psutil reports 12 physical / 14 logical CPUs. CPU count does not justify 14 GIS workers. |
| Physical RAM | 16,605,564,928 bytes = 15.47 GiB. |
| Available RAM | 1,210,769,408 bytes initially; later 1,279,795,200 bytes. About 92% in use. |
| C: storage | Total 254,782,992,384 bytes (237.28 GiB); initially free 36,421,091,328 bytes (33.92 GiB), later 36,412,035,072 bytes. Other usable volumes were not established. |
| WSL | Executable exists, but `wsl --list --quiet` reports the Windows Subsystem for Linux is not installed. |
| Container / Conda | `docker` and `conda` not found on PATH. |
| Management queries | Win32_OperatingSystem and Win32_Processor CIM queries returned access denied. Python Win32 memory calls, psutil, disk APIs and registry reads supplied the evidence above. No elevation was needed. |

Memory/storage figures are snapshots. Runtime doctor checks must measure them again before every batch. At the observed memory pressure, even a single large worker should not start.

## Python and dependency checks

Interpreter: `.venv/Scripts/python.exe`, CPython **3.12.7**, 64 bit. `.venv/pyvenv.cfg` has `include-system-site-packages = true`; NetworkX, Jinja2 and Pillow resolve from the base Python installation. The root requirements file is unpinned and does not fully specify the proposed stack. This is usable for inspection but insufficient as a reproducible environment.

| Package | Import result / version |
|---|---|
| GeoPandas / Shapely | 1.2.0 / 2.2.0 |
| Pyogrio | 0.13.0, bundled GDAL 3.12.4 |
| Rasterio | 1.5.2, bundled GDAL 3.12.2 |
| NumPy / SciPy | 2.5.4 / 1.18.1 |
| pandas / PyArrow | 3.1.0 / 26.0.0 |
| NetworkX | 3.6.1, inherited from base environment |
| Matplotlib / Pillow | 3.11.2 / 12.0.0 |
| Jinja2 / PyYAML | 3.1.6 / 6.0.3 |
| tqdm / psutil / requests | 4.70.1 / 7.2.2 / 2.34.2 |
| PyProj | 3.8.0 |
| PyOsmium (`osmium`) | Import succeeds; distribution version was not captured. Streaming PBF extraction was not tested. |
| `osgeo.gdal` | Missing: ModuleNotFoundError. |
| ReportLab / Typer / pytest | Missing: ModuleNotFoundError for each. |

These are actual runtime import results, not versions inferred from requirements. A Windows console encoding error occurred while printing notebook text; the inspection was repeated with UTF-8 stdout. Future CLI/log files must specify UTF-8.

## Functional checks and limits

Passed without writing project data:

- Enumerated GeoPackage layers and read the candidate and landmark datasets; reprojected all 1,302 candidate geometries to WGS84.
- Opened both DEMs; sampled observer elevations; read a 128 × 128 raster window and resampled it to 64 × 64 with Rasterio in memory.
- Wrote/read a two-row Parquet table in memory; rendered a Matplotlib PNG to an in-memory buffer.
- Read GPX XML, notebook JSON, NPZ arrays and QGIS archive/layout metadata; hashed selected inputs.

Not tested: GRASS startup or algorithms, standalone GDAL, full DEM integrity, PBF parsing, ReportLab generation, browser functionality or a realistic resource benchmark. Imports and tiny smoke tests do not establish production reliability.

## Native GIS execution decision

`grass`, `grass84`, `grass85`, `gdalinfo`, `gdal_viewshed` and `ogrinfo` were absent from PATH. Common Program Files, OSGeo4W and local Programs locations did not reveal a GIS installation. This is evidence of unavailability to this session, not an exhaustive scan of every disk location.

Rasterio/Pyogrio bundle different GDAL versions and do not provide `osgeo` or the GDAL CLI. Their tested operations worked together, but avoid adding an arbitrary GDAL wheel or importing GRASS's native bindings into this environment. Keep native distributions in separate processes with explicit executable paths and a controlled DLL/PROJ environment.

Recommended next-stage approach, **not installed now**:

1. Create an isolated Python 3.12 project environment without base-site inheritance. Resolve and pin compatible versions; add ReportLab, Typer and pytest. Preserve the current environment for earlier days.
2. Provision a supported native Windows GRASS distribution from the [official download entry point](https://grass.osgeo.org/download/). Record distribution URL, version, checksum, executable and dependencies. Validate unattended setup before adopting it; if unavailable, return with an alternative and its storage/setup costs.
3. Have Python launch GRASS via its [noninteractive execution interface](https://grass.osgeo.org/grass-stable/manuals/grass.html), using a separate mapset per worker. Python outside GRASS handles orchestration and exchange files; GRASS uses its own supported runtime.
4. Verify version/help output and tiny synthetic flat/ridge terrain cases for `r.viewshed`, curvature, refraction, NoData and output semantics. Verify temporary-mapset cleanup and paths containing spaces/non-ASCII characters.
5. Treat standalone GDAL as an optional preparation/independent-check tool until its installation passes tests. [GDAL viewshed documentation](https://gdal.org/en/stable/programs/gdal_viewshed.html) requires projected coordinates and warns that input NoData is not specially handled. It cannot be accepted as a drop-in fallback without validation.

The [GRASS viewshed manual](https://grass.osgeo.org/grass-stable/manuals/r.viewshed.html) exposes curvature/refraction flags and memory/scratch controls. Configure these explicitly, including observer 1.7 m and terrain target 0 m. The [horizon manual](https://grass.osgeo.org/grass-stable/manuals/r.horizon.html) documents a solar-oriented horizon with no negative angles; its output is not automatically equivalent to the proposed summit skyline. A custom, validated Python skyline metric is required.

## Resource gate

Start with one external-memory viewshed worker, an explicit 512 MiB GRASS memory setting and measured process-tree peak memory. This setting is an algorithm budget, not a hard process-memory ceiling. Require at least 4 GiB available host RAM before a realistic pilot; preserve at least 2 GiB available during execution. Pause new work if the reserve is breached. Increase concurrency only after measured headroom supports it.

Before acquisition or mosaicking, estimate download + mosaic + GRASS import + scratch + outputs and retain at least 15 GiB free. With only about 34 GiB free now, retaining every full-resolution viewshed is inappropriate. Quantitative work estimates and approval gates are in [implementation_plan.md](implementation_plan.md).

## Repository safety and audit provenance

No AGENTS.md was found in the repository or the checked ancestor locations. Existing Git status before document creation contained two untracked files: `projects/day03_polygons/data/processed/tashkent_dem_30m.tif` and `projects/day03_polygons/scripts/temp.py`. They belong to the pre-existing working state and must be preserved.

The repository README identifies `docs/` as the GitHub Pages publishing root; audit documents requested here are therefore potentially publishable on a later push. No push occurred. Keep future raw prompts, machine logs, credentials, downloads and private environment details in the new project's non-public directories. Review these four files before any eventual publication.

Evidence came from PowerShell/registry reads, Python standard library and installed package checks, local file metadata/reads, Git status/listing and the linked official documentation (accessed 2026-11-06). Full telemetry for this audit was not captured; no development duration or iteration count is claimed.
