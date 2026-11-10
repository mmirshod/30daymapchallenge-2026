import geopandas as gpd
import pytest
from shapely.geometry import Point

from beyond_the_summit.prepare import pilot_sample, validate_candidates, domain_manifest


def candidates():
    return gpd.GeoDataFrame({'id':list(range(18)),
        'observer_id':[f'node:{i}' for i in range(18)],
        'elevation_m':[1800+i*100 for i in range(18)]},
        geometry=[Point(500000+(i%6)*500,4600000+(i//6)*500) for i in range(18)],crs=32642)


def test_selection_is_stable_under_input_reordering_and_spans_elevation():
    points=candidates()
    first=pilot_sample(points)
    second=pilot_sample(points.sample(frac=1,random_state=15))
    assert first==second
    assert len({r['observer_id'] for r in first})==12
    assert [sum(r['elevation_tercile']==i for r in first) for i in [1,2,3]]==[4,4,4]


def test_scope_rejects_low_elevation_and_duplicates():
    points=candidates()
    validate_candidates(points,18,1800)
    points.loc[0,'elevation_m']=1799
    with pytest.raises(ValueError,match='elevation'):
        validate_candidates(points,18,1800)
    points.loc[0,'elevation_m']=1800
    points.loc[1,'id']=0
    with pytest.raises(ValueError,match='unique IDs'):
        validate_candidates(points,18,1800)


def test_domain_preserves_border_terrain_and_reports_missing_tiles():
    points=gpd.GeoDataFrame(geometry=[Point(70,42)],crs=4326).to_crs(32642)
    d=domain_manifest(points,50000,{})
    assert d['bounds_wgs84'][0]<70<d['bounds_wgs84'][2]
    assert d['bounds_wgs84'][1]<42<d['bounds_wgs84'][3]
    assert len(d['tiles'])>=4
    assert all(t['cached_path'] is None for t in d['tiles'])

