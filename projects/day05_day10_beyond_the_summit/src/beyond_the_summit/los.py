"""Independent sampled terrain-profile LOS checks (not a viewshed engine)."""
from __future__ import annotations

import numpy as np


def profile_visibility(distances_m, ground_m, *, observer_height_m=1.7,
                       target_height_m=0.0, refraction_coefficient=0.14286,
                       earth_radius_m=6371008.8, clearance_tolerance_m=0.0) -> dict:
    distances=np.asarray(distances_m,dtype=float)
    ground=np.asarray(ground_m,dtype=float)
    if distances.ndim!=1 or ground.shape!=distances.shape or len(distances)<3:
        raise ValueError('Profile requires aligned one-dimensional arrays with interior samples')
    if not np.isfinite(distances).all() or distances[0]!=0 or np.any(np.diff(distances)<=0):
        raise ValueError('Distances must start at zero and increase strictly')
    if not 0<=refraction_coefficient<1 or earth_radius_m<=0:
        raise ValueError('Invalid physical configuration')
    if not np.isfinite(ground).all():
        return {'visible':None,'minimum_clearance_m':None,'status':'unknown_missing_terrain'}
    corrected=ground-(1-refraction_coefficient)*distances**2/(2*earth_radius_m)
    observer=corrected[0]+observer_height_m
    target=corrected[-1]+target_height_m
    sight=observer+(target-observer)*distances/distances[-1]
    clearance=float(np.min(sight[1:-1]-corrected[1:-1]))
    return {'visible':bool(clearance>=-clearance_tolerance_m),
            'minimum_clearance_m':clearance,'status':'sampled_profile',
            'earth_radius_m':earth_radius_m,'refraction_coefficient':refraction_coefficient}
