# G5 products, 2026-11-10

All 1,302 G4 observers completed and 6,510 artifact hashes passed G5 verification. New `projects/day05_day10_beyond_the_summit/data/processed/g5/` contains full raw/component/normalized NPS rankings, Top 10, elevation bands, special winners, correlations and sensitivity outputs; complete MPS remains missing. Generated figures and projection QA are in `report/g5/`. Eighty unknown mask-boundary observations remain explicit. [G5 report](../projects/day05_day10_beyond_the_summit/docs/g5_checkpoint.md). Original Day 01-04 sources remain preserved; historical inventory follows.

# Lake exclusion and G3 outputs, 2026-11-10

The user excluded lakes from ranking; all 24 lake records remain in the new audit table with explicit exclusion flags, and lake geometry is no longer required. The 20 supplied Horizon summit landmarks remain non-lake candidates (15 within the study union), with membership/visual eligibility still unresolved. G3 now provides twelve GDAL rasters, peak-edge tables, signed true-bearing horizon profiles and LOS diagnostics; zero lakes were sampled. [Measured G3 report](../projects/day05_day10_beyond_the_summit/docs/g3_checkpoint.md). Earlier source inventories below are historical.

# G2 additions, 2026-11-10

All 1,302 100 km circles plus 60 m halo are certified against every cell in the existing 30 m mosaic; no DEM download was needed. The new project now holds a historical 2026-11-02T21:21:26Z OSM point catalogue: 2,948 in-domain peaks, 2,052 eligible >=1,800 m targets, 69 absent from the existing Uzbekistan extract, zero missing DEM samples and all observer IDs retained. Two nonpoint peak-tagged ways remain excluded QA objects. There are 44 GPX-reconciled landmarks (20 Horizon summits/24 Mirage lake points), 35 in scope; complete MPS membership/coordinates and lake geometry remain unresolved. Source query, raw responses, licences, hashes and outputs are documented in the [G2 checkpoint](../projects/day05_day10_beyond_the_summit/docs/g2_checkpoint.md). Earlier-day files remain unchanged. Historical audit follows.

# Beyond the Summit: data inventory

**2026-11-09 pilot additions:** six missing 100 km GLO-30 tiles were downloaded to `projects/day05_day10_beyond_the_summit/data/raw/dem/`, with per-file URL/remote identity/size/SHA-256 sidecars. Together with thirteen original cache tiles they supplied derived EPSG:32642 pilot mosaics: `data/interim/pilot_dem_90m.tif` (3,684 columns x 4,308 rows; 35,865,039 bytes) and `data/interim/pilot_dem_30m.tif` (11,052 x 12,924; 298,825,795 bytes), both under the new project. Exact source hashes/bounds are in their `.manifest.json` files. Computed circle/halo coverage passed for the sampled observers; this is not a certification of every regional cell. Previous Day 01–04 files remain immutable. See the new project's [pilot report](../projects/day05_day10_beyond_the_summit/docs/pilot_results.md).

Audit date: **2026-11-06, Asia/Tashkent**. All paths are repository-relative. Datasets were inspected read-only. Bounds are `(xmin, ymin, xmax, ymax)` in the stated CRS. A bounding rectangle is not proof of complete valid-data coverage.

**Scope decision, 2026-11-06:** the user explicitly confirmed >=1,800 m summits for this project. Retain the existing 1,302-candidate cohort; the conflict described below is resolved by restricting the research claim. Lower-elevation regional summits are out of scope. International target catalogue completeness remains a separate requirement.

## Observation candidates: found, but already elevation-filtered

| File / exact layer | Format; CRS | Count; bounds | Assessment |
|---|---|---|---|
| `projects/day03_polygons/data/processed/peaks_1800.gpkg` / `peaks_1800` | GeoPackage Point; EPSG:4326 | 1,302; (69.6692671, 40.6282997, 71.2690927, 42.2949036) | Original reusable candidate cohort. |
| `projects/day03_polygons/data/processed/peaks_with_ridges.gpkg` / `peaks` | GeoPackage Point; EPSG:32642 | 1,302; (556596.673, 4497735.392, 687346.861, 4684582.091) | Preferred candidate source with stable OSM `id`, coordinates, elevation provenance and ridge assignments. Explicitly select layer `peaks`. |
| `projects/day04_clusters/data/processed/peaks_clustered.gpkg` / `peak_clusters` | GeoPackage Point; EPSG:32642 | 1,302; same projected bounds | Adds DBSCAN/HDBSCAN and terrain-related cluster labels; useful for stratified sampling and interpretation. |

Current disk metadata lists only layer `peaks` in `peaks_with_ridges.gpkg`; a saved notebook output mentions older multiple-layer contents. Disk inspection takes precedence over stale notebook outputs.

Candidate checks: 1,302 unique IDs, zero exact duplicate geometries, no invalid/empty geometries, no missing `elevation_m`. Elevations span **1,800.9–4,395.5 m**; 627 use OSM elevations and 675 use DEM elevations. 1,184 lack a primary `name`; preserve multilingual aliases and display a stable ID for unnamed peaks. None of the 1,302 observer locations sampled NoData in the 30 m mosaic.

**Critical conflict:** the Day 03 preprocessing notebook explicitly constructs `peaks_1800` using `elevation_m >= 1800`. Using this cohort alone cannot answer the unrestricted question across all regional summits. No new filtering should be introduced. Approval is needed either to broaden candidates using the existing raw OSM snapshot or to limit the research claim to this cohort. An unfiltered regional peak layer was not found among inspected GeoPackages. The number of additional lower summits is unknown; do not assume it.

Use DEM ground plus observer height for geometric calculations, with a separate record of OSM height discrepancies. Do not silently treat mixed-source `elevation_m` as a consistent vertical datum.

## Elevation data

| File / collection | Actual metadata | Reuse and limitations |
|---|---|---|
| `projects/day03_polygons/data/processed/tashkent_dem_30m.tif` | GeoTIFF, 201,020,049 bytes; EPSG:32642; 7,788 columns × 8,397 rows; 30 × 30 m; float32; NoData -9999; bounds (461730, 4440690, 695370, 4692600) | Valid local pilot input, not a complete 100/150 km domain. A 256 × 256 nearest-neighbor diagnostic sample was 2.69% masked; this is not an exact full-raster NoData rate. Vertical datum not encoded in inspected tags. |
| `projects/day04_clusters/data/processed/terrain_dem_150m.tif` | GeoTIFF, 4,235,520 bytes; EPSG:32642; 1,073 × 1,447; 150 m; float32; NoData NaN; bounds (541500, 4482600, 702450, 4699650) | Existing coarse terrain context. Diagnostic sample had no masked cells; cannot establish full validity or suitability as a baseline. |
| `projects/day02_lines/data/processed/bostanlyk_dem.tif` | GeoTIFF, 79,070,422 bytes; EPSG:4326; 6,058 × 3,856; 1 arc-second; float32; NoData -9999; bounds (69.5863291, 41.2239664, 71.2691069, 42.2950775) | Local geographic mosaic; degrees are not uniform 30 m cells. Reproject before metric viewsheds. |
| `projects/day02_lines/data/raw/dem/*.tif` | **84 Copernicus-named tiles**, 3,475,854,671 bytes total; each 3,600 × 3,600, EPSG:4326, 1 arc-second; inspected NoData metadata is None | Main cache to reuse. Aggregate bounds (54.9998611, 37.0001389, 73.9998611, 46.0001389) enclose many gaps. NoData metadata alone does not rule out invalid values. |

Example raw tile: `Copernicus_DSM_COG_10_N41_00_E070_00_DEM.tif`; bounds (69.9998611, 41.0001389, 70.9998611, 42.0001389); `AREA_OR_POINT=Point`. Do not infer a 10 m resolution from the filename's `10`: measured grid spacing is 1 arc-second. The projected mosaic is PixelIsArea; account for half-cell alignment during reconstruction.

The existing `projects/day03_polygons/scripts/build_day03_dem.py` builds the 30 m EPSG:32642 mosaic from this cache, using ridge/boundary extents plus an 8 km buffer, WarpedVRT/bilinear interpolation and bounded-memory merging. Reuse its concepts, not its output path or overwrite mode. Its docstring names a different script filename, and its diagnostic samples ridge representative points only. The Day 02 downloader uses the public Copernicus S3 endpoint but has no checksum verification or true interrupted-download resume; do not run it unchanged.

The [Copernicus product description](https://dataspace.copernicus.eu/explore-data/data-collections/copernicus-contributing-missions/collections-description/COP-DEM) identifies the product vertical reference as EGM2008. Local lineage suggests this reference but does not independently certify every cached tile. The [AWS registry](https://registry.opendata.aws/copernicus-dem/) identifies the distributed product as a DSM, including surface objects, and describes public access and license links. Archive the specific release/license metadata before acquisition. Baseline terrain-only language must acknowledge the DSM approximation.

### Cross-border domain and missing tile screening

Computed from the union of buffers around all current candidates in EPSG:32642, transformed to WGS84. This is a discovery screen, not a final tile manifest: verify actual raster footprints, valid cells and resampling halo during preparation.

| Radius | Buffered domain WGS84 bounds | Nominal 1-degree cells intersecting domain | Nominal cells missing from cache |
|---|---|---:|---:|
| 50 km | (69.07801, 40.17788, 71.87402, 42.74490) | 9 | 0 |
| 100 km | (68.48097, 39.72741, 72.47848, 43.19486) | 19 | 6 |
| 150 km | (67.88034, 39.27692, 73.08238, 43.64478) | 28 | 11 |

Missing at 100 km: **N39E069, N39E070, N42E068, N42E072, N43E070, N43E071**.

Missing at 150 km: those six plus **N41E073, N42E067, N42E073, N43E069, N43E072**. These are nominal geographic cell identifiers, not verified remote object availability. Tile existence, release, response size and access have not been checked with HEAD requests. Expanded candidates or distant-landmark corridors require recalculation.

The union of actual cached raster rectangles leaves approximately 9.91% of the 100 km domain and 26.67% of the 150 km domain uncovered **by area in geographic coordinates**. These are rough screening fractions, not geodesic-area coverage measures. The 50 km domain is covered by those rectangles, subject to internal validity checks.

Only 900 / 241 / 0 candidate circles at 50 / 100 / 150 km fit entirely inside the existing 30 m mosaic's rectangle. Even these counts do not certify internal NoData-free coverage. Analyze terrain across borders without clipping it to Uzbekistan.

## Landmarks, boundaries and earlier analysis

| File / layer or asset | CRS, count, extent | Use / limitations |
|---|---|---|
| `projects/day01_points/data/processed/gorets_points.gpkg` / `gorets_points` | EPSG:4326, Point Z, 44; exact geometry bounds approximately (66.58914, 38.08219, 71.233284, 42.2533995) | 20 Horizon and 24 Mirage records, no exact duplicate XY. All 44 `ele` values null; `osmand_osm_tag_ele` absent for 24. Names, program tags and ancillary references require verification; Z is not a validated summit altitude. |
| `projects/day01_points/data/raw/favorites-21 Горизонт.gpx` | GPX XML, WGS84, 20 waypoints; (67.27887, 38.38384, 70.47401, 42.07277) | Raw provenance for Horizon; filename does not prove a complete 21-object program. |
| `projects/day01_points/data/raw/favorites-21 Мираж.gpx` | GPX XML, WGS84, 24 waypoints; (66.58914, 38.08219, 71.233284, 42.2533995) | Raw Mirage records; investigate membership/counts and object types. |
| `projects/day03_polygons/data/processed/tashkent_boundary.gpkg` / `tashkent_boundary` | EPSG:4326, Polygon, 1; (68.6403992, 40.1883097, 71.2690927, 42.2950775) | Candidate membership and study context; validate against regional boundary source. |
| `projects/day03_polygons/data/processed/ridges_with_stats.gpkg` / `ridge_statistics` | EPSG:32642, MultiPolygon, 7; (541966.956, 4497631.211, 687346.861, 4684590.817) | Context/stratification; delineated polygons, not independent visibility evidence. |
| `projects/day03_polygons/data/raw/tashkent_ridges_raw.geojson` | EPSG:4326, 7; (69.406648, 40.416667, 71.374745, 42.341277) | Original ridge geometry; some extent outside region is intentional. |
| `projects/day03_polygons/data/processed/ridge_peak_assignments.csv` | 1,302 rows, 8 columns; no geometry/CRS | Join on `id`; assignments, status and method. |
| `projects/day03_polygons/data/processed/ridge_statistics.csv` | 7 rows, 18 columns; no geometry/CRS | Existing summaries, not new analysis. |
| `projects/day04_clusters/data/processed/saddle_metrics.npz` | Six arrays of length 6,127: `edge_u`, `edge_v`, `global_saddle`, `local_1km`, `local_2km`, `local_3km` | Graph endpoints are row indices, not stable peak IDs. Reconstruct the original ordering before reuse; saddle metrics do not measure visibility. Notebook constructs an 8-neighbor, <=12 km graph. No independent serialized visibility graph was found. |
| `projects/day04_clusters/data/processed/clustering_comparison.csv` | CSV, no spatial CRS | Existing cluster comparison; secondary context, not a visibility result. Contents not audited here. |
| `projects/day02_lines/data/raw/uzbekistan-261102.osm.pbf` and identical filename under `projects/day03_polygons/data/raw/` | Two 125,361,160-byte OSM PBF files; standard OSM WGS84 coordinates; exact feature count/header extent not read | SHA-256 identical. Candidate source for unfiltered regional peaks; streaming extraction remains to be tested. Country extract does not establish cross-border completeness. |
| `projects/day02_lines/data/processed/administrative_boundaries.gpkg` | EPSG:4326: `country` 1, `regions` 14, `districts` 203, `unassigned_areas` 3 | Country/region/district bounds (55.9985531, 37.1816004, 73.2147728, 45.5906784); unassigned bounds (66.977654, 39.7273713, 71.7485307, 41.0384712). Completeness/source fields exist; validate regional selection. |
| `projects/day01_points/data/processed/tashkent_districts.gpkg` / `adm_districts` | EPSG:4326, 4 MultiPolygons; (69.3928528, 40.6922073, 71.3160019, 42.2881737) | Four districts, not the full region. Raw source `projects/day01_points/data/raw/geoBoundaries-UZB-ADM2.geojson` exists; not fully audited. |

Day 02 roads/elevation layers also exist but are not required for geometric panorama ranking: `roads_classified.gpkg` has 571,899 road features; `where_roads_end.gpkg` repeats boundaries/roads with 598 highest points and 5,801 candidates. The `elevation/tiles/` and `elevation/qa_tiles/` folders contain **84 CSVs each**, not additional DEM rasters.

## Cartography and publication assets

- QGIS archives exist for Days 01–04. Day 03 and Day 04 have 7 layers each and saved layouts `Day03 - 1` and `Day 04 -`. Inspect style/layout metadata programmatically later; no manual QGIS export is needed.
- `docs/day03/Day 03 - Report.png` and `docs/day04/Day 04 - Report.png` are 2,400 × 2,400 PNG references. They are square; the new report must adapt their style to the requested three-page landscape format. No existing PDF was found in the inspected project file inventory.
- Day 01 includes a self-contained OpenLayers/qgis2web site, symbols and terrain **image tiles**. These are cartographic assets, not numeric elevation data. Root README notes a missing temporary contour source in Day 01 QGIS archives.
- `docs/` already hosts the gallery and earlier days; `shared/` and `scripts/` contain placeholders. Do not relocate or overwrite existing outputs.

## Missing data and acquisition plan

1. **Complete elevation domain:** reuse valid cache tiles, then acquire only the missing GLO-30 cells plus interpolation halo and any separately approved landmark corridors. Python should create a manifest, inspect headers, resume verified partial downloads and check hashes/lengths. No GLO-90 substitution without approval.
2. **International peaks:** stream `natural=peak` objects from matching-date Uzbekistan, Kazakhstan, Kyrgyzstan and Tajikistan extracts as required by the actual domain. Preserve OSM type/ID, names, raw elevation and source snapshot; filter by buffered domain, not country. [Geofabrik's regional index](https://download.geofabrik.de/asia.html) provides country extracts. Resolve border overlap by IDs. OSM completeness is unknown, and a missing tag is not absence of a summit.
3. **Validated landmark registry:** obtain verified memberships/coordinates for Underground, Cascade and Snow Leopard, and reconcile the 20/24 Horizon/Mirage records. Store source evidence, object type, visual eligibility and many-to-many program membership. Unresolved or non-visible object types cannot silently count toward MPS.
4. **Provenance and permissions:** archive source release/license evidence and GPX redistribution permission. Include [OSM attribution and database license information](https://www.openstreetmap.org/copyright) in future outputs. Exact registry completeness and reuse rights remain unresolved.

Weather is deferred P2. New boundary data is optional if existing regional membership checks pass. A new DEM provider, paid data or changed resolution requires a documented user decision.

## Input fingerprints captured now

| Input | SHA-256 |
|---|---|
| Day 03 `peaks_with_ridges.gpkg` | `11300b3b3f511f0074b47b18202fd28d6998ec4b1dfb147ea0cd29ab04b5c401` |
| Day 04 `peaks_clustered.gpkg` | `173d011d38a759817c61ab06f9352fa806786724a12a854db529060c04ec6e8a` |
| Day 03 `tashkent_dem_30m.tif` | `fee4e7d8563d01af9896bf884135388f336c93af0ce4186af6b5e8364c748870` |
| Each inspected Uzbekistan PBF copy | `386e023ec89cdb432d8c064b0dd243833f459b2e53dc8b640d1f5188bebc9602` |

Full raw-cache hashing and blockwise raster validation are deferred to preparation. Prior-day processed files are not uniformly ignored/tracked; never assume a fresh clone contains local inputs.
