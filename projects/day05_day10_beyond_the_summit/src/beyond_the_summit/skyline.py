"""Signed, curvature-corrected horizon sampling for pilot convergence checks.

Angles are grid-north azimuths in the projected DEM. These diagnostic profiles
are not scored skyline prominence or production true-bearing products.
"""
from __future__ import annotations
import math
import time
import numpy as np
import rasterio
from scipy.ndimage import map_coordinates
from .runtime import config,require_resources


def horizon_profile(path,x,y,radius,step_degrees,*,observer_height=1.7,k=.14286):
    started=time.monotonic();cpu=time.process_time()
    with rasterio.open(path) as source:
        a=source.read(1);res=source.res[0];inverse=~source.transform
        col,row=inverse*(x,y)
        ground=float(map_coordinates(a,[[row-.5],[col-.5]],order=1,mode='nearest',prefilter=False)[0])
        distances=np.arange(res/2,radius,res/2,dtype='float64')
        distances=np.append(distances,radius)
        curvature=(1-k)*distances**2/(2*6371008.8)
        bearings=np.arange(0,360,step_degrees,dtype='float64')
        horizons=[];limiting=[]
        for start in range(0,len(bearings),32):
            require_resources(config())
            angle=np.deg2rad(bearings[start:start+32])
            xx=x+np.sin(angle)[:,None]*distances[None,:]
            yy=y+np.cos(angle)[:,None]*distances[None,:]
            columns=inverse.a*xx+inverse.b*yy+inverse.c-.5
            rows=inverse.d*xx+inverse.e*yy+inverse.f-.5
            z=map_coordinates(a,[rows,columns],order=1,mode='nearest',prefilter=False)
            if not np.isfinite(z).all() or np.any(z<-500):raise ValueError('Horizon ray has missing/invalid terrain')
            elevations=np.rad2deg(np.arctan2(z-ground-observer_height-curvature[None,:],distances[None,:]))
            index=np.argmax(elevations,axis=1)
            horizons.extend(elevations[np.arange(len(index)),index].tolist())
            limiting.extend(distances[index].tolist())
    return {'azimuth_grid_north_degrees':bearings.tolist(),'horizon_degrees':horizons,
            'limiting_distance_m':limiting,'angular_step_degrees':step_degrees,
            'radial_step_m':res/2,'radius_m':radius,'observer_dem_bilinear_ground_m':ground,
            'wall_seconds':time.monotonic()-started,'python_process_cpu_seconds':time.process_time()-cpu,
            'model':f'signed apparent-angle max; k={k} effective spherical Earth; bilinear DEM sampling',
            'status':'pilot diagnostic; prominence, geodesic bearings and optical visibility not validated'}
