import numpy as np
import pytest
import rasterio
from rasterio.transform import from_origin
from beyond_the_summit.pilot import crop_window,independent_profiles


def write(path,array):
    with rasterio.open(path,'w',driver='GTiff',width=array.shape[1],height=array.shape[0],count=1,
                       dtype=array.dtype,crs=32642,transform=from_origin(500000,4600000,30,30),nodata=-9999 if array.dtype==np.float32 else 255) as ds:ds.write(array,1)


def test_crop_preserves_grid_and_rejects_missing_in_circle(tmp_path):
    a=np.full((100,100),100,dtype='float32');p=tmp_path/'source.tif';write(p,a)
    with rasterio.open(p) as ds:
        cropped,tr=crop_window(ds,501500,4598500,600)
        assert cropped.shape==(44,44)
        assert (tr.c-500000)%30==0 and (4600000-tr.f)%30==0
        with pytest.raises(ValueError,match='outside'):crop_window(ds,500015,4599985,600)
    a[50,50]=-9999;write(p,a)
    with rasterio.open(p) as ds:
        with pytest.raises(ValueError,match='missing terrain'):crop_window(ds,501500,4598500,600)


def test_profile_sampling_is_deterministic_and_labels_sparse_strata(tmp_path):
    dem=tmp_path/'dem.tif';view=tmp_path/'view.tif'
    write(dem,np.full((100,100),100,dtype='float32'))
    write(view,np.ones((100,100),dtype='uint8'))
    a=independent_profiles(dem,view,501500,4598500,1000)
    b=independent_profiles(dem,view,501500,4598500,1000)
    assert a==b
    assert a['count']==36 # three range strata; no fabricated invisible class
    assert all(r['grass_visible'] for r in a['profiles'])
