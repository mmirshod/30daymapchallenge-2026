# Pilot results — 2026-11-09

Study: 1,302 mapped Tashkent summits >=1,800 m; 100 km maximum radius; one observer at a time. These are benchmark and diagnostic results, not panorama scores or rankings.

| Phase | Observers | Native wall seconds min / median / max | Peak sampled native process-tree RSS | Peak sampled scratch |
|---|---:|---:|---:|---:|
| local | 3 | 2.05 / 2.05 / 2.06 | 203 MiB | not recorded |
| 100km | 12 | 6.16 / 8.21 / 12.83 | 611 MiB | 0.03 GiB |
| 100km30 | 3 | 183.78 / 186.78 / 253.67 | 657 MiB | 6.53 GiB |

Native wall time includes fresh GRASS startup, DEM import, viewshed and export. It excludes Python profile diagnostics, skyline checks and acquisition. Scratch is sampled every three seconds and RSS every half second; these are sampled peaks. Process-tree RSS sums working sets and can include shared pages more than once.

## Independent profile checks

Point-reference diagnostics use the supplied summit XY and bilinear DEM ground. GRASS models the containing raster-cell centre. Cell-reference diagnostics use the cell centre and WGS84 semimajor axis to match that convention. Original summit coordinates are retained; the difference is not silently treated as a summit relocation. Both remain same-DEM tests, not surveyed ground truth. The +/-2 m grazing band is diagnostic.

- local: 216 profiles; point-reference agreement 99.54%; non-grazing agreement 100.00% across 188 profiles.
- 100km: 815 profiles; point-reference agreement 90.80%; non-grazing agreement 93.94% across 660 profiles.
- 100km30: 192 profiles; point-reference agreement 97.92%; non-grazing agreement 99.32% across 148 profiles.
  Matched cell-reference non-grazing agreement: 100.00%.

## Resolution comparison

| Observer | Visible terrain at 30 m | Visible terrain at 90 m | 90 m relative change |
|---|---:|---:|---:|
| node:1544318396 | 74.9 km² | 99.1 km² | +32.3% |
| node:2594726988 | 40.2 km² | 48.3 km² | +19.9% |
| node:2533272142 | 4599.1 km² | 3623.7 km² | -21.2% |

Median absolute visible-area change: **21.2%**; provisional <=10% gate: **FAIL**. Three matched cases cannot establish ranking stability.

| Observer | Angular step | P95 difference from interpolated fine profile | Maximum difference |
|---|---:|---:|---:|
| node:1544318396 | 0.25° | 0.016° | 0.104° |
| node:1544318396 | 0.1° | 0.005° | 0.034° |
| node:2594726988 | 0.25° | 0.018° | 0.072° |
| node:2594726988 | 0.1° | 0.005° | 0.032° |
| node:2533272142 | 0.25° | 0.013° | 0.055° |
| node:2533272142 | 0.1° | 0.005° | 0.037° |

Angular convergence compares circularly interpolated coarse horizons against 0.05-degree profiles. Diagnostic azimuths are grid-north; production true-bearing conversion, skyline prominence, smoothing and metric definitions still require validation.

## Cost interpretation and remaining gates

Pilot radii and areas use EPSG:32642 projected map metres. Geodesic distortion and true-bearing conversion remain production validation tasks.


### Independent GDAL comparison

| Observer | GDAL compute/output | Visible-pixel intersection over union with GRASS | Cell-reference non-grazing LOS agreement |
|---|---:|---:|---:|
| node:1544318396 | 0.83 s | 95.24% | 98.21% |
| node:2594726988 | 0.84 s | 92.58% | 85.19% |
| node:2533272142 | 0.91 s | 96.78% | 95.35% |

GDAL timing covers compute and initial output only, not common-grid alignment, Python diagnostics or summit/landmark calculations. The fast result is not accepted solely on speed or whole-circle pixel agreement. Visible-pixel IoU emphasizes the small visible subset; GRASS itself is a model reference, not ground truth. Production backend remains unchanged.

- 100km: scaling the measured median native time to 1,302 observers gives **3.0 hours for the native terrain stage alone**. This is an extrapolation from 12 cases, not a measured full-run duration; it excludes skyline, peak/landmark LOS, retries and publication.
- 100km30: scaling the measured median native time to 1,302 observers gives **67.6 hours for the native terrain stage alone**. This is an extrapolation from 3 cases, not a measured full-run duration; it excludes skyline, peak/landmark LOS, retries and publication.
- No baseline resolution or full production run is approved by this report. Check area differences against the provisional 10% threshold and independent non-grazing profiles against 99%; retain failed thresholds rather than relaxing them.
- International peak-catalogue completeness, landmark verification, optical distinguishability, scoring and production skyline validation remain outstanding.
- Google Drive destination/quota and Python upload authentication are not configured. Pilot artifacts remain bounded local files; no cloud transfer or deletion of earlier-day inputs occurred.
- Native synthetic prerequisites passed five cases; pilot unit tests and command history are documented in the agent log.


## Diagnostic horizon profiles

![Measured pilot horizons](../report/pilot/horizons.png)
