"""One GDAL observer per process, bounded crop and exact output mask."""
from __future__ import annotations

import json
from pathlib import Path
import sys
import time

import numpy as np
import rasterio
from rasterio.windows import Window, from_bounds
from osgeo import gdal

from .runtime import atomic_json, config, require_resources


def execute(request: dict) -> dict:
    started = time.monotonic()
    cfg = config()
    work = Path(request['work'])
    settings = request['settings']
    x, y = request['coordinates']
    radius = settings['radius_m']
    gdal.UseExceptions()
    gdal.SetCacheMax(int(settings['cache_mb']*2**20))

    def guard(*args):
        require_resources(cfg)
        if time.monotonic()-started > settings['timeout_seconds']:
            raise TimeoutError('GDAL observer exceeded time budget')
        size = sum(p.stat().st_size for p in work.iterdir() if p.is_file())
        if size > settings['scratch_limit_bytes']:
            raise RuntimeError('GDAL observer scratch limit exceeded')
        return 1

    guard()
    with rasterio.open(request['dem']) as source:
        t = source.transform
        if (source.crs is None or not source.crs.is_projected
                or abs(source.crs.linear_units_factor[1]-1) > 1e-8):
            raise ValueError('Viewshed requires a projected metric DEM')
        if (source.count != 1 or t.b != 0 or t.d != 0 or t.a <= 0 or t.e >= 0
                or not np.isclose(t.a, -t.e, rtol=0, atol=1e-8)):
            raise ValueError('Require a single-band north-up square-cell DEM')
        if source.scales != (1.0,) or source.offsets != (0.0,):
            raise ValueError('DEM scale/offset must be materialized before visibility')
        cell = t.a
        halo = radius+2*cell
        b = source.bounds
        if not (b.left <= x-halo and x+halo <= b.right
                and b.bottom <= y-halo and y+halo <= b.top):
            raise ValueError('Incomplete DEM coverage for observer circle and two-cell halo')
        w = from_bounds(x-halo, y-halo, x+halo, y+halo, t)
        col, row = int(np.floor(w.col_off)), int(np.floor(w.row_off))
        width = int(np.ceil(w.col_off+w.width))-col
        height = int(np.ceil(w.row_off+w.height))-row
        window = Window(col, row, width, height)
        transform = source.window_transform(window)
        profile = source.profile
        profile.update(width=width, height=height, transform=transform, driver='GTiff',
                       tiled=True, blockxsize=256, blockysize=256, compress='deflate')
        crop = work/'dem.tif'
        with rasterio.open(crop, 'w', **profile) as target:
            for _, block in target.block_windows(1):
                guard()
                values = source.read(1, window=Window(col+block.col_off,row+block.row_off,block.width,block.height), masked=True)
                xx = transform.c+(block.col_off+np.arange(block.width)+.5)*cell
                yy = transform.f-(block.row_off+np.arange(block.height)+.5)*cell
                support = np.hypot(xx[None,:]-x, yy[:,None]-y) <= halo
                invalid = np.ma.getmaskarray(values) | ~np.isfinite(np.asarray(values))
                if np.any(support & invalid):
                    raise ValueError('Missing terrain within observer circle/halo; no substitution allowed')
                target.write(values.data, 1, window=block)
        observer_row, observer_col = source.index(x,y)
        ground = float(source.read(1,window=Window(observer_col,observer_row,1,1))[0,0])
        effective_x, effective_y = source.xy(observer_row,observer_col)
        crs = source.crs.to_string()
    # No resampling: GDAL's clipped result is mapped back to the crop grid.
    ds = gdal.Open(str(crop))
    compute_started = time.monotonic()
    raw_path = work/'raw.tif'
    raw = gdal.ViewshedGenerate(ds.GetRasterBand(1), 'GTiff', str(raw_path),
        ['COMPRESS=DEFLATE','TILED=YES'], x,y,settings['observer_height_m'],0.0,
        1,0,255,255,1-settings['refraction_coefficient'] if settings['earth_curvature'] else 0.0,
        gdal.GVM_Edge, radius+cell, guard)
    if raw is None:
        raise RuntimeError('GDAL viewshed returned no dataset')
    raw = None
    ds = None
    compute_seconds = time.monotonic()-compute_started
    profile.update(dtype='uint8', nodata=255)
    visible = cells = 0
    with rasterio.open(raw_path) as raw, rasterio.open(work/'viewshed.tif','w',**profile) as target:
        offset_col = round((transform.c-raw.transform.c)/cell)
        offset_row = round((raw.transform.f-transform.f)/cell)
        if (raw.crs.to_string() != crs or not np.isclose(raw.transform.a,cell)
                or abs(transform.c-(raw.transform.c+offset_col*cell)) > 1e-6
                or abs(transform.f-(raw.transform.f-offset_row*cell)) > 1e-6):
            raise RuntimeError('GDAL output is not aligned to the input grid')
        for _, block in target.block_windows(1):
            guard()
            a = raw.read(1,window=Window(offset_col+block.col_off,offset_row+block.row_off,
                         block.width,block.height),boundless=True,fill_value=255)
            xx = transform.c+(block.col_off+np.arange(block.width)+.5)*cell
            yy = transform.f-(block.row_off+np.arange(block.height)+.5)*cell
            inside = np.hypot(xx[None,:]-x,yy[:,None]-y) <= radius
            if np.any(inside & ~np.isin(a,[0,1])):
                raise RuntimeError('Unknown GDAL output within analysis radius')
            a[~inside] = 255
            target.write(a,1,window=block)
            visible += int(np.sum(inside & (a == 1)))
            cells += int(inside.sum())
    guard()
    details = {'compute_and_initial_output_seconds': compute_seconds,
               'worker_wall_seconds': time.monotonic()-started,
               'visible_cells': visible, 'in_radius_cells': cells,
               'visible_area_km2': visible*cell*cell/1e6,
               'effective_observer_cell': {'row':observer_row,'col':observer_col,
                   'x':effective_x,'y':effective_y,'ground_m':ground},
               'output_grid': {'crs':crs,'transform':list(transform),'width':width,'height':height},
               'curvature_coefficient': 1-settings['refraction_coefficient'] if settings['earth_curvature'] else 0.0,
               'input_vertical_units_assumed': 'metres; source lineage must verify',
               'radius_convention': 'input-coordinate projected cell-centre mask',
               'gdal_version':gdal.VersionInfo()}
    atomic_json(work/'result.json',details)
    return details


if __name__ == '__main__':
    execute(json.loads(Path(sys.argv[1]).read_text(encoding='utf-8')))
