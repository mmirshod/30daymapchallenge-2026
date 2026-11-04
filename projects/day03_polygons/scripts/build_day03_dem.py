"""Build a 30 m UTM GeoTIFF for Day 03 from Day 02 Copernicus DEM tiles.

Run from any working directory:
    python projects/day03_polygons/scripts/build_dem_30m.py

Dependencies: geopandas, rasterio, numpy, shapely
No standalone GDAL Python package required.
"""

from __future__ import annotations

import argparse
from contextlib import ExitStack
from pathlib import Path

import geopandas as gpd
import numpy as np
import rasterio
from rasterio.enums import Resampling
from rasterio.merge import merge
from rasterio.vrt import WarpedVRT
from rasterio.warp import transform_bounds
from rasterio.windows import Window
from shapely.geometry import box

CRS = "EPSG:32642"
NODATA = -9999.0


def main() -> None:
    parser = argparse.ArgumentParser(description="Build 30 m Copernicus DEM mosaic for Day 03")
    parser.add_argument("--resolution", type=float, default=30.0, help="Output pixel size in metres")
    parser.add_argument("--buffer-km", type=float, default=8.0, help="Buffer around study polygons in km")
    parser.add_argument("--mem-limit", type=int, default=128, help="Rasterio merge working memory MiB")
    parser.add_argument("--overwrite", action="store_true", help="Replace an existing output")
    args = parser.parse_args()

    day03 = Path(__file__).resolve().parents[1]
    projects = day03.parent
    dem_dir = projects / "day02_lines" / "data" / "raw" / "dem"
    ridges_file = day03 / "data" / "processed" / "ridges_with_stats.gpkg"
    boundary_file = day03 / "data" / "processed" / "tashkent_boundary.gpkg"
    output = day03 / "data" / "processed" / "tashkent_dem_30m.tif"

    if args.resolution <= 0 or args.buffer_km < 0:
        parser.error("Resolution must be positive and buffer must be nonnegative")
    if not ridges_file.exists() or not boundary_file.exists():
        raise FileNotFoundError("Need ridges_with_stats.gpkg and tashkent_boundary.gpkg in Day 03 processed")
    tiles = sorted(dem_dir.glob("*.tif"))
    if not tiles:
        raise FileNotFoundError(f"No DEM TIFF tiles found in {dem_dir}")
    if output.exists() and not args.overwrite:
        raise FileExistsError(f"Output exists: {output}. Use --overwrite to replace")

    ridges = gpd.read_file(ridges_file).to_crs(CRS)
    boundary = gpd.read_file(boundary_file).to_crs(CRS)
    # Union of both extents: maps include the whole Tashkent region and all manually
    # delineated ridge polygons, even where a ridge extends across the boundary.
    left = min(ridges.total_bounds[0], boundary.total_bounds[0]) - args.buffer_km * 1000
    bottom = min(ridges.total_bounds[1], boundary.total_bounds[1]) - args.buffer_km * 1000
    right = max(ridges.total_bounds[2], boundary.total_bounds[2]) + args.buffer_km * 1000
    top = max(ridges.total_bounds[3], boundary.total_bounds[3]) + args.buffer_km * 1000

    res = args.resolution
    bounds = (
        np.floor(left / res) * res,
        np.floor(bottom / res) * res,
        np.ceil(right / res) * res,
        np.ceil(top / res) * res,
    )
    width = int(round((bounds[2] - bounds[0]) / res))
    height = int(round((bounds[3] - bounds[1]) / res))
    print(f"Target extent (UTM): {bounds}")
    print(f"Raster: {width:,} × {height:,} pixels; raw float32 ≈ {width * height * 4 / 2**20:.1f} MiB")

    output.parent.mkdir(parents=True, exist_ok=True)
    vrt_sources = []
    with ExitStack() as stack:
        for tile in tiles:
            src = stack.enter_context(rasterio.open(tile))
            tile_bounds = transform_bounds(src.crs, CRS, *src.bounds, densify_pts=21)
            if not box(*tile_bounds).intersects(box(*bounds)):
                continue
            vrt = stack.enter_context(WarpedVRT(
                src,
                crs=CRS,
                resampling=Resampling.bilinear,
                src_nodata=src.nodata,
                nodata=NODATA,
            ))
            vrt_sources.append(vrt)
        if not vrt_sources:
            raise RuntimeError("None of the source DEM tiles intersects the requested output extent")
        print(f"Using {len(vrt_sources)} of {len(tiles)} source tiles")
        merge(
            vrt_sources,
            bounds=bounds,
            res=(res, res),
            nodata=NODATA,
            dtype="float32",
            resampling=Resampling.nearest,  # VRT already interpolates each source
            method="first",
            target_aligned_pixels=True,
            mem_limit=args.mem_limit,
            dst_path=str(output),
            dst_kwds={
                "driver": "GTiff",
                "compress": "deflate",
                "predictor": 3,
                "tiled": True,
                "blockxsize": 512,
                "blockysize": 512,
                "BIGTIFF": "IF_SAFER",
            },
        )

    # Validate coverage at ridge polygon representative points as a quick diagnostic.
    with rasterio.open(output, "r+") as ds:
        test_pts = ridges.geometry.representative_point()
        values = list(ds.sample([(p.x, p.y) for p in test_pts], masked=True))
        missing = sum(np.ma.is_masked(v[0]) or float(v[0]) == NODATA for v in values)
        print(f"Ridge representative points with missing DEM: {missing}/{len(test_pts)}")
        print(f"CRS: {ds.crs} | pixel size: {ds.res} | file: {output}")
        if missing:
            print("WARNING: Some ridge zones lack coverage; inspect source DEM tile coverage before mapping.")
        # Overviews make the GeoTIFF much quicker to pan/zoom in QGIS.
        factors = [f for f in (2, 4, 8, 16, 32) if min(ds.width, ds.height) // f >= 1]
        ds.build_overviews(factors, Resampling.average)
        ds.update_tags(ns="rio_overview", resampling="average")

    print("Done. Transfer the output GeoTIFF to your Mac via Google Drive.")


if __name__ == "__main__":
    main()