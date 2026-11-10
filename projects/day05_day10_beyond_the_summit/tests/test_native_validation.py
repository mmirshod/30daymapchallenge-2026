import numpy as np
import pytest
import rasterio
from rasterio.transform import from_origin

from beyond_the_summit.validation import viewshed


def test_missing_terrain_rejected_before_native_execution(tmp_path):
    p=tmp_path/'gap.tif'
    a=np.ones((8,8),dtype='float32');a[3,3]=-9999
    with rasterio.open(p,'w',driver='GTiff',width=8,height=8,count=1,dtype='float32',
                       crs=32642,transform=from_origin(500000,4600000,30,30),nodata=-9999) as ds:
        ds.write(a,1)
    with pytest.raises(ValueError,match='missing terrain'):
        viewshed(p,tmp_path/'output.tif',(500015,4599985))
