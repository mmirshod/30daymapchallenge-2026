import numpy as np
import rasterio
from rasterio.transform import from_origin
from beyond_the_summit import skyline


def test_flat_terrain_preserves_signed_negative_horizon(tmp_path,monkeypatch):
    monkeypatch.setattr(skyline,'require_resources',lambda *a,**k:None)
    p=tmp_path/'flat.tif';a=np.full((100,100),100,dtype='float32')
    with rasterio.open(p,'w',driver='GTiff',width=100,height=100,count=1,dtype='float32',
                       crs=32642,transform=from_origin(500000,4600000,30,30)) as ds:ds.write(a,1)
    result=skyline.horizon_profile(p,501500,4598500,600,90)
    assert len(result['horizon_degrees'])==4
    assert all(angle<0 for angle in result['horizon_degrees'])
    assert result['limiting_distance_m']==[600.0]*4
