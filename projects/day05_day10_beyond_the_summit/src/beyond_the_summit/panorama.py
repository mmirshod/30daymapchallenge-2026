"""Bounded panorama summaries and diagnostic signed skyline extraction."""
from __future__ import annotations

import math
import time
import numpy as np
import pandas as pd
from pyproj import Transformer, Geod
import rasterio
from rasterio.windows import from_bounds
from scipy.ndimage import map_coordinates, uniform_filter1d, minimum_filter1d

from .los import profile_visibility
from .runtime import require_resources


def terrain_summary(path, cfg):
    started=time.monotonic()
    bands=cfg['analysis']['distance_bands_m']
    counts=np.zeros(len(bands)-1,dtype=np.int64)
    visible=np.zeros_like(counts)
    sectors=np.zeros(36,dtype=np.int64)
    far_sectors=np.zeros_like(sectors)
    x,y=cfg['_observer_xy']
    with rasterio.open(path) as view:
        cell=view.res[0]
        for index,(_,window) in enumerate(view.block_windows(1)):
            if index%50==0:require_resources(cfg)
            a=view.read(1,window=window)
            xx=view.transform.c+(window.col_off+np.arange(window.width)+.5)*cell-x
            yy=view.transform.f-(window.row_off+np.arange(window.height)+.5)*cell-y
            distance=np.hypot(xx[None,:],yy[:,None])
            in_circle=distance<=bands[-1]
            if np.any(in_circle&~np.isin(a,[0,1])):raise ValueError('Unknown terrain inside analysis circle')
            for j,(lo,hi) in enumerate(zip(bands[:-1],bands[1:])):
                selected=in_circle&(distance>=lo if j==0 else distance>lo)&(distance<=hi)
                counts[j]+=int(selected.sum());visible[j]+=int((selected&(a==1)).sum())
            az=(np.rad2deg(np.arctan2(xx[None,:],yy[:,None]))+360)%360
            sector=(az//10).astype(int)
            mask=in_circle&(a==1)
            sectors+=np.bincount(sector[mask],minlength=36)
            far_sectors+=np.bincount(sector[mask&(distance>=20000)],minlength=36)
    return {'visible_area_km2':float(visible.sum()*cell*cell/1e6),
        'visible_cells':int(visible.sum()),'circle_cells':int(counts.sum()),
        'distance_bands':[{'lower_m':lo,'upper_m':hi,'cells':int(n),'visible_cells':int(v),
                          'visible_area_km2':float(v*cell*cell/1e6),'visible_fraction':float(v/n) if n else None}
                         for lo,hi,n,v in zip(bands[:-1],bands[1:],counts,visible)],
        'ten_degree_grid_north_sector_visible_cells':sectors.tolist(),
        'ten_degree_sectors_with_visible_ground_beyond_20km':int((far_sectors>0).sum()),
        'wall_seconds':time.monotonic()-started,'area_method':'projected cell area; not geodesic area'}


def peak_edges(view_path,observer,targets,cfg):
    x,y=observer['x'],observer['y']
    distances=np.hypot(targets.geometry.x.to_numpy()-x,targets.geometry.y.to_numpy()-y)
    subset=targets[(distances<=cfg['analysis']['radius_m'])&(targets.target_id!=observer['observer_id'])].copy()
    subset['distance_projected_m']=distances[(distances<=cfg['analysis']['radius_m'])&(targets.target_id!=observer['observer_id'])]
    transformer=Transformer.from_crs(targets.crs,4326,always_xy=True)
    lon,lat=transformer.transform(x,y)
    lons,lats=transformer.transform(subset.geometry.x.to_numpy(),subset.geometry.y.to_numpy())
    az,_,geodesic=Geod(ellps='WGS84').inv(np.full(len(subset),lon),np.full(len(subset),lat),lons,lats)
    with rasterio.open(view_path) as view:
        values=np.array([int(v[0]) for v in view.sample([(p.x,p.y) for p in subset.geometry])])
    edges=pd.DataFrame({'observer_id':observer['observer_id'],'target_id':subset.target_id.to_numpy(),
        'target_x':subset.geometry.x.to_numpy(),'target_y':subset.geometry.y.to_numpy(),
        'distance_projected_m':subset.distance_projected_m.to_numpy(),'distance_geodesic_m':geodesic,
        'bearing_true_degrees':(az+360)%360,'target_elevation_m':subset.elevation_m.to_numpy(),
        'target_ground_dem_m':subset.ground_dem_m.to_numpy(),
        'visible':pd.array([bool(v) if v in (0,1) else None for v in values],dtype='boolean'),
        'status':['visible_ground_proxy' if v==1 else 'hidden_ground_proxy' if v==0 else 'unknown_at_mask_boundary' for v in values],
        'target_reference':'DEM-cell ground, not a corrected surveyed summit height'})
    seen=edges[edges.visible.fillna(False)]
    stats={'eligible_targets_in_radius':len(edges),'visible_peak_ground_proxies':len(seen),
        'unknown_targets':int(edges.visible.isna().sum()),
        'visible_peak_mean_elevation_m':float(seen.target_elevation_m.mean()) if len(seen) else None,
        'visible_peak_max_distance_geodesic_m':float(seen.distance_geodesic_m.max()) if len(seen) else None,
        'ten_degree_true_bearing_sectors_occupied':int((seen.bearing_true_degrees//10).nunique()),
        'self_target_excluded':True,'definition':'OSM point sampled from binary GDAL ground-target raster'}
    return edges,stats


def skyline_and_los(dem_path,view_path,observer,edges,cfg,*,step_degrees=.1):
    started=time.monotonic();cpu=time.process_time()
    x,y=observer['x'],observer['y'];radius=cfg['analysis']['radius_m']
    with rasterio.open(view_path) as view,rasterio.open(dem_path) as dem:
        window=from_bounds(*view.bounds,dem.transform).round_offsets().round_lengths()
        a=dem.read(1,window=window)
        transform=dem.window_transform(window);inverse=~transform;res=dem.res[0]
        row,col=dem.index(x,y);effective_x,effective_y=dem.xy(row,col)
        local_col,local_row=inverse*(effective_x,effective_y)
        ground=float(a[int(local_row),int(local_col)])
        x,y=effective_x,effective_y
        distances=np.append(np.arange(res/2,radius,res/2,dtype=float),radius)
        coefficient=1-cfg['analysis']['refraction_coefficient'] if cfg['analysis']['earth_curvature'] else 0
        correction=coefficient*distances**2/(2*6378137.0)
        bearings=np.arange(0,360,step_degrees)
        horizons=[];limits=[]
        for start in range(0,len(bearings),32):
            require_resources(cfg)
            angle=np.deg2rad(bearings[start:start+32])
            xx=x+np.sin(angle)[:,None]*distances[None,:]
            yy=y+np.cos(angle)[:,None]*distances[None,:]
            columns=inverse.a*xx+inverse.c-.5;rows=inverse.e*yy+inverse.f-.5
            z=map_coordinates(a,[rows,columns],order=1,mode='nearest',prefilter=False)
            if not np.isfinite(z).all() or np.any(z<-500):raise ValueError('Invalid terrain on skyline ray')
            angles=np.rad2deg(np.arctan2(z-ground-cfg['analysis']['observer_height_m']-correction,distances))
            j=np.argmax(angles,axis=1)
            horizons.extend(angles[np.arange(len(j)),j].tolist());limits.extend(distances[j].tolist())
        limiting=np.asarray(limits)
        tx=x+np.sin(np.deg2rad(bearings))*limiting
        ty=y+np.cos(np.deg2rad(bearings))*limiting
        transformer=Transformer.from_crs(dem.crs,4326,always_xy=True)
        lon,lat=transformer.transform(x,y);lons,lats=transformer.transform(tx,ty)
        az,_,geo_distance=Geod(ellps='WGS84').inv(np.full(len(tx),lon),np.full(len(tx),lat),lons,lats)
        # Explicitly diagnostic local angular contrast, not topographic prominence.
        smooth=uniform_filter1d(np.asarray(horizons),size=max(1,round(.5/step_degrees)),mode='wrap')
        baseline=minimum_filter1d(smooth,size=2*round(5/step_degrees)+1,mode='wrap')
        contrast=smooth-baseline
        peaks=(smooth>np.roll(smooth,1))&(smooth>=np.roll(smooth,-1))&(contrast>=.1)
        profile={'azimuth_grid_north_degrees':bearings.tolist(),'azimuth_true_degrees':((az+360)%360).tolist(),
            'horizon_degrees':horizons,'limiting_distance_projected_m':limits,
            'limiting_distance_geodesic_m':geo_distance.tolist(),'limiting_x':tx.tolist(),'limiting_y':ty.tolist(),
            'angular_step_degrees':step_degrees,'radial_step_m':res/2,
            'effective_observer_x':x,'effective_observer_y':y,'effective_ground_dem_m':ground,
            'observer_reference':'DEM cell centre, with original summit coordinates retained separately',
            'curvature_coefficient':coefficient,'earth_radius_m':6378137.0,
            'model':'signed bilinear radial maximum; true bearing to limiting terrain point',
            'diagnostic_metrics':{'horizon_p95_minus_p05_degrees':float(np.percentile(horizons,95)-np.percentile(horizons,5)),
                'mean_absolute_smoothed_slope_degrees_per_degree':float(np.abs(smooth-np.roll(smooth,1)).mean()/step_degrees),
                'local_angular_features':int(peaks.sum()),'maximum_local_contrast_degrees':float(contrast.max()),
                'definition':'0.5-degree circular smoothing, +/-5-degree minimum baseline, local maxima >=0.1-degree contrast; provisional'},
            'wall_seconds':time.monotonic()-started,'python_cpu_seconds':time.process_time()-cpu}
        # Independent targeted rays: both engine classes and all distance bands.
        selected=[]
        known=edges[edges.visible.notna()&(edges.distance_projected_m>3*res)]
        for lo,hi in zip(cfg['analysis']['distance_bands_m'][:-1],cfg['analysis']['distance_bands_m'][1:]):
            for visible in (False,True):
                group=known[(known.distance_projected_m>lo)&(known.distance_projected_m<=hi)&(known.visible==visible)]
                selected.extend(group.sort_values('target_id').head(4).index.tolist())
        remaining=known.drop(index=selected).sort_values('target_id')
        selected.extend(remaining.head(max(0,24-len(selected))).index.tolist())
        checks=[]
        for _,edge in edges.loc[selected].iterrows():
            require_resources(cfg)
            target_row,target_col=dem.index(edge.target_x,edge.target_y)
            target_x,target_y=dem.xy(target_row,target_col)
            length=math.hypot(target_x-x,target_y-y)
            d=np.linspace(0,length,max(3,math.ceil(length/(res/2))+1))
            px=x+(target_x-x)*d/length;py=y+(target_y-y)*d/length
            z=map_coordinates(a,[inverse.e*py+inverse.f-.5,inverse.a*px+inverse.c-.5],order=1,mode='nearest',prefilter=False)
            if np.any(z<-500):raise ValueError('Invalid terrain on independent LOS ray')
            check=profile_visibility(d,z,observer_height_m=cfg['analysis']['observer_height_m'],
                refraction_coefficient=cfg['analysis']['refraction_coefficient'],earth_radius_m=6378137)
            checks.append({'target_id':edge.target_id,'gdal_visible':bool(edge.visible),
                'profile_visible':check['visible'],'clearance_m':check['minimum_clearance_m'],
                'near_grazing_2m':abs(check['minimum_clearance_m'])<=2,
                'agrees':bool(edge.visible)==check['visible']})
    nongrazing=[c for c in checks if not c['near_grazing_2m']]
    diagnostics={'checks':checks,'count':len(checks),'non_grazing_count':len(nongrazing),
        'agreement_fraction':sum(c['agrees'] for c in checks)/len(checks) if checks else None,
        'non_grazing_agreement_fraction':sum(c['agrees'] for c in nongrazing)/len(nongrazing) if nongrazing else None,
        'limitations':'same-DSM diagnostic; deterministic class/distance sample, not unbiased accuracy or surveying',
        'combined_skyline_los_wall_seconds':time.monotonic()-started}
    return profile,diagnostics
