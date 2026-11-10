from copy import deepcopy
import geopandas as gpd
import numpy as np
import pytest
import rasterio
from rasterio.transform import from_origin
from shapely.geometry import Point

from beyond_the_summit.data_readiness import parse_elevation,parse_roster,certify_coverage
from beyond_the_summit.runtime import config


@pytest.mark.parametrize('value,expected',[('1800',1800),('1,850 m',None),('1800.5 м',1800.5),
    ('2,450.5',None),('7000 ft',None),('1800;1900',None),(None,None),('nan',None),('99999',None)])
def test_conservative_source_elevation(value,expected):
    # Comma is a decimal delimiter only; mixed delimiters are rejected.
    assert parse_elevation(value)==expected


def test_official_group_numbers_not_individual_object_count():
    html='<script>1. fake</script><h3>21 озеро</h3><p>1. Тузкан</p><p>2. Нижний Ихнач</p><p>2. Верхний Ихнач</p><h3>ДОКАЗАТЕЛЬСТВА</h3><p>3. not a lake</p>'
    entries=parse_roster(html,'Mirage')
    assert len(entries)==3
    assert {e['ordinal'] for e in entries}=={1,2}


def test_exact_circle_union_coverage(tmp_path,monkeypatch):
    from beyond_the_summit import data_readiness as module
    monkeypatch.setattr(module,'require_resources',lambda *a,**k:None)
    monkeypatch.setattr(module,'REPOSITORY',tmp_path)
    cfg=deepcopy(config());cfg['analysis']['radius_m']=100
    points=gpd.GeoDataFrame({'observer_id':['one','two']},geometry=[Point(350,650),Point(650,350)],crs=32642)
    dem=tmp_path/'dem.tif'
    def save(a):
        with rasterio.open(dem,'w',driver='GTiff',width=100,height=100,count=1,dtype='float32',
                crs=32642,transform=from_origin(0,1000,10,10),nodata=-9999) as ds:ds.write(a,1)
    a=np.zeros((100,100),dtype='float32');a[0,0]=-9999;save(a)
    result=certify_coverage(dem,points,cfg)
    assert result['passed'] and result['invalid_cells_entire_mosaic']==1
    a[35,35]=-9999;save(a)
    result=certify_coverage(dem,points,cfg)
    assert not result['passed'] and result['invalid_cells_within_circle_union_and_halo']==1
    points.geometry=[Point(50,50),Point(650,350)];save(np.zeros((100,100),dtype='float32'))
    assert not certify_coverage(dem,points,cfg)['passed']


@pytest.mark.parametrize('remark',[None,'runtime error: Query timed out'])
def test_overpass_cache_and_incomplete_response(tmp_path,monkeypatch,remark):
    import json
    from beyond_the_summit import data_readiness as module
    monkeypatch.setattr(module,'RAW',tmp_path)
    monkeypatch.setattr(module,'require_resources',lambda *a,**k:None)
    class Response:
        def __enter__(self):return self
        def __exit__(self,*a):pass
        def raise_for_status(self):pass
        def iter_content(self,size):
            yield json.dumps({'elements':[],'remark':remark} if remark else {'elements':[]}).encode()
    calls=[]
    def post(*a,**k):calls.append(a);return Response()
    monkeypatch.setattr(module.requests,'post',post)
    class Log:
        def event(self,*a,**k):pass
    if remark:
        with pytest.raises(RuntimeError,match='acquisition failed'):
            module.fetch_overpass((68,40,72,43),'2026-11-02T00:00:00Z',config(),Log())
        assert not list(tmp_path.glob('*.source.json'))
    else:
        module.fetch_overpass((68,40,72,43),'2026-11-02T00:00:00Z',config(),Log())
        module.fetch_overpass((68,40,72,43),'2026-11-02T00:00:00Z',config(),Log())
        assert len(calls)==1
        response=next(p for p in tmp_path.glob('peaks_*.json') if '.source.' not in p.name)
        response.write_bytes(b'corrupt cache')
        with pytest.raises(ValueError,match='provenance'):
            module.fetch_overpass((68,40,72,43),'2026-11-02T00:00:00Z',config(),Log())
