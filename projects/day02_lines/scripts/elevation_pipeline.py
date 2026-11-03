
from pathlib import Path
import json
import math

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
from pyproj import Geod
from shapely.geometry import box

# ============================================================
# CONFIGURATION
# ============================================================

PROJECT_DIR = Path(__file__).resolve().parent.parent
PROCESSED = PROJECT_DIR / "data" / "processed"
DEM_DIR = PROJECT_DIR / "data" / "raw" / "dem"

OUT = PROCESSED / "elevation"
TILES_OUT = OUT / "tiles"
QA_OUT = OUT / "qa_tiles"
LOG_OUT = OUT / "logs"

STEP_M = 30
BATCH_SIZE = 40_000
TOP_K = 10
PIPELINE_VERSION = 1

GEOD = Geod(ellps="WGS84")

CATEGORIES = ("asphalt", "conventional", "all_drivable")

OUTPUT_COLUMNS = [
    "district_id", "district_name", "osm_id", "highway",
    "elevation_m", "lon", "lat", "is_restricted",
    "category", "tile"
]

QA_COLUMNS = [
    "osm_id", "highway", "elevation_m", "lon", "lat",
    "is_restricted", "territory_status", "tile"
]


# ============================================================
# GEOMETRY & ROAD SAMPLING
# ============================================================

def as_bool(series):
    return (
        series.astype("string")
        .str.strip()
        .str.lower()
        .isin(["true", "1", "yes"])
    )


def iter_lines(geometry):
    if geometry is None or geometry.is_empty:
        return

    if geometry.geom_type == "LineString":
        yield geometry

    elif geometry.geom_type in (
        "MultiLineString", "GeometryCollection"
    ):
        for part in geometry.geoms:
            yield from iter_lines(part)


def sampled_vertices(line):
    """
    Deterministic geodesic sampling.
    Includes original OSM vertices and intermediate points
    spaced no more than STEP_M apart.
    """
    coords = list(line.coords)

    if not coords:
        return

    yield coords[0][0], coords[0][1]

    for start, end in zip(coords[:-1], coords[1:]):
        x0, y0 = start[:2]
        x1, y1 = end[:2]

        _, _, distance = GEOD.inv(x0, y0, x1, y1)

        if distance > 0:
            pieces = max(
                1, math.ceil(distance / STEP_M)
            )

            if pieces > 1:
                yield from GEOD.npts(
                    x0, y0, x1, y1, pieces - 1
                )

        yield x1, y1


def iter_batches(road_subset, bounds):
    left, bottom, right, top = bounds
    records = []

    cols = [
        "id", "highway", "is_confirmed_asphalt",
        "is_conventional", "is_access_restricted",
        "geometry"
    ]

    for row in road_subset[cols].itertuples(
        index=False, name=None
    ):
        (
            osm_id, highway, asphalt,
            conventional, restricted, geometry
        ) = row

        for line in iter_lines(geometry):
            for lon, lat in sampled_vertices(line):

                # Half-open bounds avoid duplicate tile assignment
                if not (
                    left <= lon < right
                    and bottom < lat <= top
                ):
                    continue

                records.append((
                    str(osm_id),
                    highway,
                    bool(asphalt),
                    bool(conventional),
                    bool(restricted),
                    lon,
                    lat,
                ))

                if len(records) >= BATCH_SIZE:
                    yield pd.DataFrame.from_records(
                        records,
                        columns=[
                            "osm_id", "highway",
                            "is_asphalt", "is_conventional",
                            "is_restricted", "lon", "lat"
                        ]
                    )
                    records = []

    if records:
        yield pd.DataFrame.from_records(
            records,
            columns=[
                "osm_id", "highway",
                "is_asphalt", "is_conventional",
                "is_restricted", "lon", "lat"
            ]
        )


# ============================================================
# DEM ELEVATION EXTRACTION
# ============================================================

def sample_dem(batch, dem, pixels):
    t = dem.transform

    assert abs(t.b) < 1e-12 and abs(t.d) < 1e-12, (
        "Expected north-up DEM"
    )

    xs = batch.lon.to_numpy(dtype="float64")
    ys = batch.lat.to_numpy(dtype="float64")

    cols = np.floor(
        (xs - t.c) / t.a
    ).astype(np.int64)

    rows = np.floor(
        (ys - t.f) / t.e
    ).astype(np.int64)

    ok = (
        (cols >= 0) & (cols < dem.width)
        & (rows >= 0) & (rows < dem.height)
    )

    elevations = np.full(
        len(batch), np.nan, dtype="float32"
    )

    if ok.any():
        values = pixels[rows[ok], cols[ok]]

        elevations[ok] = np.asarray(
            np.ma.filled(values, np.nan),
            dtype="float32"
        )

    elevations[~np.isfinite(elevations)] = np.nan

    # Exclude impossible DEM values and common bad sentinels
    elevations[
        (elevations < -100) | (elevations > 7000)
    ] = np.nan

    return elevations


# ============================================================
# ADMINISTRATIVE ASSIGNMENT
# ============================================================

def assign_districts(batch, districts, country_shape):
    points = gpd.GeoDataFrame(
        batch.reset_index(drop=True).copy(),
        geometry=gpd.points_from_xy(
            batch.lon, batch.lat
        ),
        crs="EPSG:4326"
    )

    points["sample_id"] = np.arange(len(points))

    joined = gpd.sjoin(
        points,
        districts[
            ["district_id", "district_name", "geometry"]
        ],
        how="left",
        predicate="within"
    )

    # Flag overlaps rather than arbitrarily choosing a district
    ambiguous_ids = set(
        joined.loc[
            joined.duplicated("sample_id", keep=False),
            "sample_id"
        ]
    )

    joined.loc[
        joined["sample_id"].isin(ambiguous_ids),
        ["district_id", "district_name"]
    ] = pd.NA

    joined = (
        joined.drop_duplicates("sample_id")
        .sort_values("sample_id")
        .drop(columns=["index_right"], errors="ignore")
    )

    missing = joined["district_id"].isna()
    joined["territory_status"] = "assigned"

    if missing.any():
        inside = joined.loc[
            missing
        ].geometry.intersects(country_shape)

        joined.loc[
            missing, "territory_status"
        ] = np.where(
            inside.to_numpy(),
            "unassigned_inside",
            "outside_or_unresolved"
        )

    joined.loc[
        joined["sample_id"].isin(ambiguous_ids),
        "territory_status"
    ] = "ambiguous"

    return joined


# ============================================================
# CANDIDATES & CHECKPOINTS
# ============================================================

def collect_candidates(df, tile):
    found = []
    assigned = df.loc[df["district_id"].notna()]

    for category in CATEGORIES:

        if category == "asphalt":
            subset = assigned.loc[assigned["is_asphalt"]]

        elif category == "conventional":
            subset = assigned.loc[
                assigned["is_conventional"]
            ]

        else:
            subset = assigned

        if subset.empty:
            continue

        best = (
            subset.sort_values(
                "elevation_m", ascending=False
            )
            .drop_duplicates(["district_id", "osm_id"])
            .groupby("district_id", sort=False)
            .head(TOP_K)
            .copy()
        )

        best["category"] = category
        best["tile"] = tile

        found.append(best[OUTPUT_COLUMNS])

    return found


def collect_qa(df, tile):
    missing = df.loc[df["district_id"].isna()]

    if missing.empty:
        return []

    best = (
        missing.sort_values(
            "elevation_m", ascending=False
        )
        .drop_duplicates(
            ["territory_status", "osm_id"]
        )
        .groupby("territory_status", sort=False)
        .head(TOP_K)
        .copy()
    )

    best["tile"] = tile

    return [best[QA_COLUMNS]]


def save_csv_atomic(df, path):
    path.parent.mkdir(parents=True, exist_ok=True)

    temp = path.with_suffix(path.suffix + ".tmp")

    df.to_csv(temp, index=False)
    temp.replace(path)


# ============================================================
# TILE PROCESSING
# ============================================================

def process_tile(
    tile_path, roads, districts, country_shape
):
    tile = tile_path.stem

    csv_path = TILES_OUT / f"{tile}.csv"
    qa_path = QA_OUT / f"{tile}.csv"
    log_path = LOG_OUT / f"{tile}.json"

    if (
        log_path.exists()
        and csv_path.exists()
        and qa_path.exists()
    ):
        print(f"SKIP {tile}", flush=True)
        return

    print(f"PROCESS {tile}", flush=True)

    results = []
    qa = []
    statuses = {}

    total_samples = 0
    valid_samples = 0

    with rasterio.open(tile_path) as dem:

        if dem.crs.to_epsg() != 4326:
            raise ValueError(
                f"Unexpected CRS: {tile_path}: {dem.crs}"
            )

        pixels = dem.read(1, masked=True)
        tile_geom = box(*dem.bounds)

        indices = roads.sindex.query(
            tile_geom,
            predicate="intersects"
        )

        subset = roads.iloc[indices]

        for batch in iter_batches(subset, dem.bounds):
            total_samples += len(batch)

            batch["elevation_m"] = sample_dem(
                batch, dem, pixels
            )

            batch = batch.dropna(
                subset=["elevation_m"]
            )

            valid_samples += len(batch)

            if batch.empty:
                continue

            assigned = assign_districts(
                batch, districts, country_shape
            )

            for key, value in assigned[
                "territory_status"
            ].value_counts().items():
                statuses[key] = (
                    statuses.get(key, 0) + int(value)
                )

            results.extend(
                collect_candidates(assigned, tile)
            )

            qa.extend(collect_qa(assigned, tile))

    if results:
        r = pd.concat(results, ignore_index=True)

        r = (
            r.sort_values(
                "elevation_m", ascending=False
            )
            .drop_duplicates([
                "district_id", "category", "osm_id"
            ])
            .groupby(
                ["district_id", "category"], sort=False
            )
            .head(TOP_K)
        )
    else:
        r = pd.DataFrame(columns=OUTPUT_COLUMNS)

    if qa:
        q = pd.concat(qa, ignore_index=True)

        q = (
            q.sort_values(
                "elevation_m", ascending=False
            )
            .drop_duplicates([
                "territory_status", "osm_id"
            ])
            .groupby(
                "territory_status", sort=False
            )
            .head(TOP_K)
        )
    else:
        q = pd.DataFrame(columns=QA_COLUMNS)

    save_csv_atomic(r, csv_path)
    save_csv_atomic(q, qa_path)

    log = {
        "tile": tile,
        "road_segments": int(len(subset)),
        "samples": total_samples,
        "valid_samples": valid_samples,
        "status_counts": statuses,
        "candidate_rows": len(r),
        "qa_rows": len(q),
        "step_m": STEP_M,
    }

    log_path.parent.mkdir(
        parents=True, exist_ok=True
    )

    temp = log_path.with_suffix(".tmp")

    temp.write_text(
        json.dumps(
            log, ensure_ascii=False, indent=2
        ),
        encoding="utf-8"
    )

    temp.replace(log_path)

    print(
        f"DONE {tile}: {valid_samples:,} valid; "
        f"{statuses}",
        flush=True
    )


# ============================================================
# NATIONAL AGGREGATION
# ============================================================

def aggregate_all(districts):

    files = sorted(TILES_OUT.glob("*.csv"))

    rows = [
        pd.read_csv(
            path,
            dtype={
                "osm_id": "string",
                "district_id": "string"
            }
        )
        for path in files
    ]

    rows = [x for x in rows if not x.empty]

    if not rows:
        raise RuntimeError("No results found")

    candidates = pd.concat(rows, ignore_index=True)

    top = (
        candidates.sort_values(
            "elevation_m", ascending=False
        )
        .drop_duplicates(
            ["district_id", "category", "osm_id"]
        )
        .groupby(
            ["district_id", "category"], sort=False
        )
        .head(TOP_K)
        .copy()
    )

    save_csv_atomic(
        top, OUT / "top_road_candidates.csv"
    )

    maxima = (
        top.sort_values(
            "elevation_m", ascending=False
        )
        .drop_duplicates(
            ["district_id", "category"]
        )
        .copy()
    )

    save_csv_atomic(
        maxima, OUT / "highest_road_points.csv"
    )

    # Include districts with no valid measurements
    base = districts[
        ["district_id", "district_name"]
    ].drop_duplicates().copy()

    cats = pd.DataFrame({
        "category": list(CATEGORIES)
    })

    all_combos = base.merge(cats, how="cross")

    summary = all_combos.merge(
        maxima[
            [
                "district_id", "category",
                "elevation_m", "osm_id",
                "lon", "lat", "highway", "is_restricted"
            ]
        ],
        on=["district_id", "category"],
        how="left"
    ).rename(columns={
        "elevation_m": "max_elevation_m"
    })

    save_csv_atomic(
        summary, OUT / "district_elevation_stats.csv"
    )

    # Ready-to-use layers for QGIS
    for data, filename, layer in [
        (
            top,
            "top_road_candidates.gpkg",
            "top_candidates"
        ),
        (
            maxima,
            "highest_road_points.gpkg",
            "highest_points"
        )
    ]:
        path = OUT / filename

        if path.exists():
            path.unlink()

        geom = gpd.points_from_xy(
            data.lon, data.lat
        )

        gdf = gpd.GeoDataFrame(
            data, geometry=geom, crs="EPSG:4326"
        )

        gdf.to_file(
            path,
            layer=layer,
            driver="GPKG",
            engine="pyogrio"
        )

    # Unassigned QA: highest distinct roads by status
    qa_files = sorted(QA_OUT.glob("*.csv"))

    qa_rows = [
        pd.read_csv(
            f, dtype={"osm_id": "string"}
        )
        for f in qa_files
    ]

    qa_rows = [x for x in qa_rows if not x.empty]

    if qa_rows:
        qa_data = pd.concat(
            qa_rows, ignore_index=True
        )

        qa_data = (
            qa_data.sort_values(
                "elevation_m", ascending=False
            )
            .drop_duplicates(
                ["territory_status", "osm_id"]
            )
            .groupby(
                "territory_status", sort=False
            )
            .head(100)
        )

        save_csv_atomic(
            qa_data,
            OUT / "unassigned_top_candidates.csv"
        )

    print("\nNational top-20:\n")

    print(
        maxima.nlargest(20, "elevation_m")[
            [
                "district_name", "category",
                "elevation_m", "osm_id", "highway"
            ]
        ].to_string(index=False)
    )

    print(f"\nSaved results to: {OUT}")


# ============================================================
# MAIN
# ============================================================

def main():

    OUT.mkdir(parents=True, exist_ok=True)

    for path in (TILES_OUT, QA_OUT, LOG_OUT):
        path.mkdir(parents=True, exist_ok=True)

    roads_path = (
        PROCESSED / "roads_classified.gpkg"
    )

    admin_path = (
        PROCESSED / "administrative_boundaries.gpkg"
    )

    tile_paths = sorted(
        DEM_DIR.glob(
            "Copernicus_DSM_COG_10_*_DEM.tif"
        )
    )

    if not tile_paths:
        raise FileNotFoundError(
            f"No Copernicus DEM tiles found in {DEM_DIR}"
        )

    # Prevent accidental mixing of different input versions
    signature = {
        "version": PIPELINE_VERSION,
        "step_m": STEP_M,
        "top_k": TOP_K,
        "inputs": {
            str(p): [
                p.stat().st_size,
                p.stat().st_mtime_ns
            ]
            for p in [
                roads_path, admin_path, *tile_paths
            ]
        }
    }

    manifest = OUT / "manifest.json"

    if manifest.exists():
        previous = json.loads(
            manifest.read_text(encoding="utf-8")
        )

        if previous != signature:
            raise RuntimeError(
                "Inputs/settings changed. "
                "Move or delete data/processed/elevation "
                "to restart."
            )
    else:
        if any(LOG_OUT.glob("*.json")):
            raise RuntimeError(
                "Old cache exists without manifest."
            )

        manifest.write_text(
            json.dumps(signature, indent=2),
            encoding="utf-8"
        )

    print("Loading inputs...", flush=True)

    roads = gpd.read_file(
        roads_path,
        layer="roads_classified"
    ).to_crs(4326)

    for col in [
        "is_confirmed_asphalt",
        "is_conventional",
        "is_access_restricted"
    ]:
        roads[col] = as_bool(roads[col])

    roads["is_tunnel"] = as_bool(roads["is_tunnel"])

    print("Excluded tunnel segments:", roads["is_tunnel"].sum())

    roads = roads.loc[
        ~roads["is_tunnel"]
    ].copy()

    districts = gpd.read_file(
        admin_path,
        layer="districts"
    ).to_crs(4326)

    districts["district_id"] = (
        districts["osm_id"].astype("string")
    )

    districts["district_name"] = (
        districts["name"].astype("string")
    )

    country = gpd.read_file(
        admin_path,
        layer="country"
    ).to_crs(4326)

    country_shape = country.geometry.union_all()

    print(
        f"{len(roads):,} roads; "
        f"{len(districts)} districts; "
        f"{len(tile_paths)} DEM tiles",
        flush=True
    )

    for i, tile in enumerate(tile_paths, start=1):
        print(
            f"[{i}/{len(tile_paths)}]",
            end=" ",
            flush=True
        )

        process_tile(
            tile,
            roads,
            districts,
            country_shape
        )

    aggregate_all(districts)


if __name__ == "__main__":
    main()
