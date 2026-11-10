"""Validate and stage existing sources without rewriting earlier-day files."""
from __future__ import annotations

import math
from pathlib import Path
import re

import geopandas as gpd
import numpy as np
import rasterio
from shapely.geometry import box

from .runtime import PROJECT, REPOSITORY, Run, atomic_json, config, fingerprint


def tile_name(lat: int, lon: int) -> str:
    return f'Copernicus_DSM_COG_10_{"N" if lat>=0 else "S"}{abs(lat):02d}_00_{"E" if lon>=0 else "W"}{abs(lon):03d}_00_DEM'


def domain_manifest(points: gpd.GeoDataFrame, radius_m: int, cached: dict[tuple[int,int], Path]) -> dict:
    # Include a 120 m interpolation halo around the approved radius domain.
    domain = gpd.GeoSeries([points.geometry.buffer(radius_m+120).union_all()],crs=points.crs).to_crs(4326).iloc[0]
    left,bottom,right,top = domain.bounds
    tiles=[]
    for lat in range(math.floor(bottom),math.ceil(top)):
        for lon in range(math.floor(left),math.ceil(right)):
            if not box(lon,lat,lon+1,lat+1).intersects(domain):
                continue
            name=tile_name(lat,lon)
            tiles.append({'id':name,'lat':lat,'lon':lon,'cached_path':str(cached[(lat,lon)].relative_to(REPOSITORY)) if (lat,lon) in cached else None,
                          'url':f'https://copernicus-dem-30m.s3.eu-central-1.amazonaws.com/{name}/{name}.tif'})
    return {'radius_m':radius_m,'interpolation_halo_m':120,'bounds_wgs84':list(domain.bounds),'tiles':tiles}


def validate_candidates(points: gpd.GeoDataFrame, expected: int, minimum: float) -> None:
    if points.crs is None:
        raise ValueError('Candidates have no CRS')
    if len(points)!=expected or points.id.nunique()!=expected:
        raise ValueError('Candidate count or unique IDs differ from approved cohort')
    if points.geometry.is_empty.any() or points.geometry.isna().any() or (~points.is_valid).any():
        raise ValueError('Invalid candidate geometry')
    if not points.geom_type.eq('Point').all() or points.geometry.duplicated().any():
        raise ValueError('Candidates must be unique points')
    if not np.isfinite(points.elevation_m).all() or (points.elevation_m<minimum).any():
        raise ValueError('Invalid or out-of-scope candidate elevation')


def pilot_sample(points: gpd.GeoDataFrame, per_tercile: int=4) -> list[dict]:
    """Deterministic elevation terciles plus farthest-point spatial spread."""
    ordered=points.sort_values(['elevation_m','id']).copy()
    groups=np.array_split(np.arange(len(ordered)),3)
    result=[]
    for tercile,indices in enumerate(groups):
        group=ordered.iloc[indices].sort_values('id').reset_index(drop=True)
        xy=np.column_stack([group.geometry.x,group.geometry.y])
        # First point farthest from tercile centroid; remaining points maximize
        # minimum distance to selected points. Sorting makes ties deterministic.
        distances=((xy-xy.mean(axis=0))**2).sum(axis=1)
        chosen=[]
        for _ in range(min(per_tercile,len(group))):
            distances[chosen]=-1
            chosen.append(int(np.argmax(distances)))
            distances=np.min([((xy-xy[j])**2).sum(axis=1) for j in chosen],axis=0)
        for j in chosen:
            row=group.iloc[j]
            result.append({'observer_id':str(row.observer_id),'osm_id':int(row.id),
                           'elevation_tercile':tercile+1,'elevation_m':float(row.elevation_m),
                           'x':float(row.geometry.x),'y':float(row.geometry.y)})
    return result


def prepare_existing(run: Run, cfg: dict | None=None) -> dict:
    cfg=cfg or config();study=cfg['study']
    source=REPOSITORY/study['candidate_file'];dem=REPOSITORY/study['dem_file']
    points=gpd.read_file(source,layer=study['candidate_layer']).to_crs(cfg['analysis']['crs'])
    validate_candidates(points,study['expected_observers'],study['minimum_elevation_m'])
    boundary=gpd.read_file(REPOSITORY/study['boundary_file'],layer=study['boundary_layer']).to_crs(points.crs).geometry.union_all()
    # Numerical reprojection at the boundary can shift points by submillimetres.
    outside=~points.geometry.apply(boundary.buffer(0.01).covers)
    if outside.any():
        raise ValueError(f'{int(outside.sum())} candidates outside region beyond 1 cm tolerance')
    with rasterio.open(dem) as raster:
        values=np.ma.concatenate(list(raster.sample([(p.x,p.y) for p in points.geometry],masked=True)))
        if np.ma.getmaskarray(values).any() or not np.isfinite(values).all():
            raise ValueError('Candidate DEM ground contains missing or invalid elevations')
        points['ground_dem_m']=np.asarray(values,dtype=float)
    points['observer_id']=points.osm_type.astype(str)+':'+points.id.astype(str)
    points['observer_top_dem_m']=points.ground_dem_m+cfg['analysis']['observer_height_m']
    # Compact approved-cohort artifact; retain source attributes in immutable source.
    columns=['observer_id','id','elevation_m','elevation_source','ele_osm','ele_dem','ground_dem_m','observer_top_dem_m','name','name:ru','name:en','ridge_name','geometry']
    output=PROJECT/'data/processed/observers.parquet';output.parent.mkdir(parents=True,exist_ok=True)
    temporary=output.with_suffix('.partial.parquet');points[columns].to_parquet(temporary,index=False);temporary.replace(output)
    cached={}
    for path in (REPOSITORY/study['dem_cache']).glob('*.tif'):
        match=re.search(r'N(\d+)_00_E(\d+)',path.name)
        if match:cached[tuple(map(int,match.groups()))]=path
    manifest={'schema_version':1,'candidate_source':study['candidate_file'],
              'candidate_sha256':fingerprint(source),'dem_sha256':fingerprint(dem),
              'candidate_count':len(points),'scope':study['scope'],
              'dem_vertical_reference':'EGM2008 inferred from product lineage; local metadata not certified',
              'domains':[domain_manifest(points,r,cached) for r in sorted(set(
                  [cfg['analysis']['radius_m'],*cfg['analysis']['sensitivity_radii_m']]))]}
    atomic_json(PROJECT/'data/processed/source_manifest.json',manifest)
    sample=pilot_sample(points);atomic_json(PROJECT/'data/processed/pilot_observers.json',sample)
    landmarks=gpd.read_file(REPOSITORY/study['landmark_file'],layer=study['landmark_layer'])
    summary={'observer_count':len(points),'minimum_elevation_m':float(points.elevation_m.min()),
             'maximum_elevation_m':float(points.elevation_m.max()),'candidate_source_sha256':manifest['candidate_sha256'],
             'pilot_observer_ids':[p['observer_id'] for p in sample],
             'landmark_records':len(landmarks),'landmark_program_counts':landmarks.program.value_counts().to_dict(),
             'landmark_registry_validated':False,'cross_border_dem_validated':False,
             'missing_tiles_by_radius':{str(d['radius_m']):[t['id'] for t in d['tiles'] if t['cached_path'] is None] for d in manifest['domains']},
             'status':'local_sources_validated; complete-data readiness pending'}
    atomic_json(PROJECT/'data/processed/preparation.json',summary)
    run.event('artifact',path=str(output.relative_to(PROJECT)),sha256=fingerprint(output),observers=len(points))
    return summary

