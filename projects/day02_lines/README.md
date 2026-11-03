# Day 02 — Lines | Where the Roads End

**30DayMapChallenge 2026 · Day 2: Lines · Uzbekistan**

> **How high can roads take you in Uzbekistan?**

This project examines the maximum elevation of mapped roads in Uzbekistan, comparing roads explicitly tagged as asphalt, conventional OSM road classes, and all potentially drivable roads (including tracks). Results are summarized by administrative district and will be visualized in QGIS.

**Status:** Analysis completed; highest-elevation candidates require final QA. QGIS map design and export are in progress.

## Research questions

- What is the highest elevation reached by a road explicitly tagged `surface=asphalt`?
- How much higher do conventional mapped roads extend?
- How much higher do mapped tracks extend beyond the conventional road network?
- Which administrative districts contain the highest roads in each category?

## Preliminary findings

| Category | Highest sampled elevation | District | OSM road class | OSM way |
| --- | ---: | --- | --- | --- |
| Confirmed asphalt | **2,447 m** | Zomin | `primary` | [529045942](https://www.openstreetmap.org/way/529045942) |
| Conventional roads | **3,080 m** | Pop | `unclassified` | [512550512](https://www.openstreetmap.org/way/512550512) |
| All potentially drivable roads | **3,420 m** | Pop | `track` | [266410404](https://www.openstreetmap.org/way/266410404) |

Values are rounded from the raster sampling results and are **provisional mapped-road elevation estimates**, not independently verified elevations or guarantees of vehicle access. The Zomin asphalt-road candidate was visually checked as the road toward the lower Zaamin cable-car station. A segment of OSM way 266410404 crosses into Kyrgyzstan; the reported maximum was assigned to Pop district, but border geometry remains an important QA consideration.

Across **203 administrative districts**, elevation samples were found for conventional roads and all potentially drivable roads in all 203 districts; confirmed asphalt observations were found in **192**. Absence of an asphalt result means **no qualifying OSM-tagged asphalt sample**, not necessarily absence of asphalt roads.

## Road classification

The three categories intentionally **overlap** and are not strictly nested:

| Category | Working definition |
| --- | --- |
| **Confirmed asphalt** | Potentially drivable OSM road with `surface=asphalt` |
| **Conventional roads** | Eligible OSM road classes such as `primary`, `secondary`, `tertiary`, `unclassified`, `residential`, `living_street`, `service` and associated road links; excludes `track` |
| **All potentially drivable** | Conventional-road classes plus `highway=track` |

The categories describe **OSM mapping and road classes**, not verified road condition, public access, vehicle capability, or travel suitability. Explicit access restrictions are retained as QA attributes. Missing `surface`, `smoothness`, `tracktype`, or access tags are **not** treated as negative evidence.

## Data sources

| Dataset | Source | Usage |
| --- | --- | --- |
| Road network and tags | [OpenStreetMap](https://www.openstreetmap.org/) via Uzbekistan PBF snapshot `uzbekistan-261102.osm.pbf` (2026-11-02) | Geometry and classification |
| Administrative boundaries | OpenStreetMap boundary relations, processed to GeoPackage | District (ADM2) assignment and regional context |
| Elevation | [Copernicus DEM GLO-30](https://registry.opendata.aws/copernicus-dem/) | Elevation sampling |

The analysis uses **83 DEM tiles** (approximately **3.44 GB** locally). The administrative GeoPackage includes **203 districts**, **14 regional entities**, and a QA layer for unassigned areas. Karakalpakstan is tagged `admin_level=3` in the source OSM relations and grouped with regions in the processed layer. Some boundaries were reconstructed from incomplete source relations; see the administrative boundary QA report distributed with the boundary dataset.

## Methodology

1. **Explore OSM roads:** inspect `highway`, `surface`, `tracktype`, `smoothness`, and access-tag completeness.
2. **Classify roads:** preserve eligible potentially drivable roads and their metadata; keep access restrictions flagged instead of discarding unknown values.
3. **Prepare boundaries:** extract/reconstruct OSM administrative polygons and retain geometry-quality warnings.
4. **Sample elevation:** generate reproducible geodesic samples along original OSM line geometries at intervals no greater than **30 m**, including original vertices. Extract DEM elevation by tile, without constructing a nationwide raster mosaic.
5. **Exclude tunnels from surface-based elevation calculations:** a DEM measures the terrain **above** a tunnel, not the road inside it. Tunnel geometries remain available for display.
6. **Assign districts and aggregate:** spatially join sample points to districts; calculate highest sampled elevation by district and road category, and retain the top 10 distinct OSM ways per district/category for QA.
7. **Validate candidates:** inspect high-elevation roads, access tags, bridges, tunnel flags, and boundary ambiguities before publishing definitive claims.

The national elevation pipeline caches per-tile intermediate CSVs and logs to permit resuming a run. Its manifest is intended to prevent mixing output from different source files or pipeline settings.

### Key limitations

- **Sparse surface tagging:** Approximately **10% of the mapped road length** in the preliminary EDA had a populated `surface` value. This is why “confirmed asphalt” is a conservative mapping-based indicator, not the true extent of asphalt roads.
- **Mapped ≠ drivable:** `highway=track`, `unclassified`, and other road classes do not guarantee accessibility or suitability for ordinary passenger cars.
- **DEM ≠ road survey:** GLO-30 provides surface elevations; bridges, steep slopes, inaccuracies in line positioning, and raster resolution can affect results.
- **Tunnels:** excluded from elevation sampling after identifying a false high result on the A373 Kamchik tunnel; they remain in the mapping layer.
- **Boundaries:** administrative relations in the national extract were not uniformly complete. Reconstructed polygons and unresolved/border points must remain flagged for QA. A result falling within a reconstructed country polygon is not independent proof of legal border status.
- **Sampling:** reported maxima are the highest **sampled** elevations, not an exhaustive continuous maximum along every road.

## Project layout

```text
projects/day02_lines/
├── data/
│   ├── raw/                      # OSM PBF, DEM tiles (not committed)
│   └── processed/                # Classified roads, boundaries, elevation outputs
├── notebooks/
│   ├── 01_osm_exploration.ipynb
│   ├── 02_road_classification.ipynb
│   ├── 03_administrative_boundaries.ipynb
│   ├── 04_elevation_analysis.ipynb
│   └── 05_prepare_qgis_layers.ipynb
├── scripts/
│   └── elevation_pipeline.py
├── qgis/                         # QGIS project and working GIS layers
├── exports/                      # Final rendered map(s)
├── requirements.txt
└── README.md
```

Names shown above reflect the planned workflow; adjust them if your actual notebook or script filenames differ.

## Main analysis outputs

- `data/processed/roads_classified.gpkg` — tagged road segments and flags.
- `data/processed/administrative_boundaries.gpkg` — country, regions, districts, and boundary QA layers.
- `data/processed/elevation/district_elevation_stats.csv` — district × category maxima.
- `data/processed/elevation/highest_road_points.gpkg` — highest sample for each district/category.
- `data/processed/elevation/top_road_candidates.gpkg` — highest distinct road candidates for QA.
- `data/processed/where_roads_end.gpkg` — consolidated mapping dataset (**~183 MB**), containing `country`, `regions`, `districts`, `roads`, `highest_points`, and `top_candidates`.

The final cartographic export will be placed in `exports/` after QGIS styling and layout are completed.

## Running and viewing

This project was developed with **Python/Jupyter** for data processing and **QGIS** for cartography. Python dependencies include `geopandas`, `pandas`, `numpy`, `pyrosm`, `pyogrio`, `rasterio`, `pyproj`, `shapely`, `requests`, and `matplotlib`.

1. Obtain the OSM PBF and DEM tiles, and place them under `data/raw/` using the paths expected by your notebooks/scripts.
2. Run the exploration, classification, and boundary-preparation stages, or use the already processed GeoPackages.
3. Execute `scripts/elevation_pipeline.py` after preparing the classified roads, boundaries, and DEM tiles.
4. Run `05_prepare_qgis_layers.ipynb` to assemble `where_roads_end.gpkg`.
5. Open the QGIS project and load the GeoPackage. Use **relative paths** for portability between Windows and macOS.

### Large files and GitHub

Raw PBF/DEM datasets and the ~183 MB consolidated GeoPackage are intentionally **not committed to Git**. Transfer these separately (e.g., via Google Drive), and place `where_roads_end.gpkg` at `data/processed/where_roads_end.gpkg` unless the QGIS project has been updated to a different relative path. Commit scripts, notebooks, documentation, QGIS project files, and final rendered exports.

**Processed GeoPackage:** _Add your Google Drive download link here after uploading the 183 MB file._

## Attribution

- **Roads and administrative boundaries:** © [OpenStreetMap contributors](https://www.openstreetmap.org/copyright), available under the [ODbL](https://opendatacommons.org/licenses/odbl/).
- **Elevation:** [Copernicus DEM GLO-30](https://dataspace.copernicus.eu/explore-data/data-collections/copernicus-contributing-missions/collections-description/COP-DEM). Consult the dataset's applicable attribution and redistribution terms before publishing derived raster products.

---

**30DayMapChallenge 2026 — Day 02: Lines**  
*Where the Roads End: How High Can Roads Take You in Uzbekistan?*
