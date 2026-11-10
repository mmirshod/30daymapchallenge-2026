import numpy as np
from beyond_the_summit.los import profile_visibility


def test_flat_earth_profile_and_ridge_blockage():
    d=np.linspace(0,900,61);z=np.full(len(d),100.0)
    assert profile_visibility(d,z)['visible']
    z[len(z)//2]=200
    assert not profile_visibility(d,z)['visible']
    assert profile_visibility(d,z,observer_height_m=300)['visible']


def test_curvature_and_equal_height_reciprocity():
    d=np.linspace(0,40000,161);z=np.full(len(d),100.0)
    assert not profile_visibility(d,z)['visible']
    z=np.array([100,102,101,108,104,100],dtype=float);d=np.linspace(0,3000,len(z))
    a=profile_visibility(d,z,observer_height_m=1.7,target_height_m=1.7)
    b=profile_visibility(d,z[::-1],observer_height_m=1.7,target_height_m=1.7)
    assert a['visible']==b['visible']
    assert abs(a['minimum_clearance_m']-b['minimum_clearance_m'])<1e-8


def test_missing_terrain_is_unknown_not_clear():
    result=profile_visibility([0,100,200],[100,np.nan,100])
    assert result['visible'] is None
    assert result['status']=='unknown_missing_terrain'
