from dataclasses import replace
import json
from pathlib import Path
import sys
import os
from types import SimpleNamespace

import numpy as np
import pytest
import rasterio
from rasterio.transform import from_origin

from beyond_the_summit.gdal_viewshed import ViewshedSettings, generate_viewshed
from beyond_the_summit import native
from beyond_the_summit import gdal_viewshed as adapter, gdal_worker


@pytest.fixture
def in_process(monkeypatch):
    """Tiny real GDAL fixtures, without another GIS interpreter under low RAM.

    Mock only OS resource gates and process transport. Separate integration
    coverage below retains the real subprocess and actual resource gates.
    """
    monkeypatch.setattr(adapter,'require_resources',lambda *a,**k:None)
    monkeypatch.setattr(gdal_worker,'require_resources',lambda *a,**k:None)
    def execute(arguments,**kwargs):
        try:
            gdal_worker.execute(json.loads(Path(arguments[-1]).read_text(encoding='utf-8')))
        except (ValueError,RuntimeError) as error:
            raise RuntimeError(str(error)) from error
        return SimpleNamespace(measurements={'transport':'in-process test double; not a subprocess benchmark'})
    monkeypatch.setattr(adapter,'run_native',execute)


def terrain(path, *, ridge=False, cell=30, crs='EPSG:32642', missing=False):
    a = np.full((241,241),100,dtype='float32')
    if ridge:
        a[:,120] = 200
    if missing:
        a[120,110] = -9999
    with rasterio.open(path,'w',driver='GTiff',width=241,height=241,count=1,
                       dtype='float32',crs=crs,transform=from_origin(500000,4650000,cell,cell),nodata=-9999) as ds:
        ds.write(a,1)
    return path


def sample(path,x,y):
    with rasterio.open(path) as ds:
        return int(next(ds.sample([(x,y)]))[0])


@pytest.mark.parametrize('ridge,height,expected',[(False,1.7,1),(True,1.7,0),(True,300,1)])
def test_actual_gdal_flat_ridge_and_elevated_observer(tmp_path,in_process,ridge,height,expected):
    dem=terrain(tmp_path/'dem.tif',ridge=ridge)
    output=tmp_path/'view.tif'
    settings=ViewshedSettings(radius_m=2000,observer_height_m=height)
    report=generate_viewshed(dem,output,(502715,4646385),settings=settings)
    assert sample(output,504515,4646385)==expected
    assert report['status']=='complete'
    assert report['details']['effective_observer_cell']['col']==90
    with rasterio.open(output) as ds:
        a=ds.read(1)
        rr,cc=np.indices(a.shape)
        xx=ds.transform.c+(cc+.5)*30
        yy=ds.transform.f-(rr+.5)*30
        inside=np.hypot(xx-502715,yy-4646385)<=2000
        assert np.all(a[~inside]==255)
        assert np.all(np.isin(a[inside],[0,1]))
        assert ds.nodata==255


def test_curvature_and_checkpoint_integrity(tmp_path,in_process):
    dem=terrain(tmp_path/'flat.tif',cell=1000)
    output=tmp_path/'view.tif'
    settings=ViewshedSettings(radius_m=60000,earth_curvature=False)
    first=generate_viewshed(dem,output,(600500,4529500),settings=settings)
    assert sample(output,640500,4529500)==1
    assert generate_viewshed(dem,output,(600500,4529500),settings=settings)['reused']
    curved=generate_viewshed(dem,output,(600500,4529500),settings=replace(settings,earth_curvature=True))
    assert not curved['reused'] and curved['signature']!=first['signature']
    assert sample(output,640500,4529500)==0
    # Corrupt outputs cannot pass the checkpoint hash; the adapter repairs them.
    output.write_bytes(b'interrupted output')
    repaired=generate_viewshed(dem,output,(600500,4529500),settings=replace(settings,earth_curvature=True))
    assert not repaired['reused']
    assert sample(output,640500,4529500)==0


@pytest.mark.parametrize('bad', ['nodata','geographic','edge'])
def test_reject_invalid_terrain_without_publishing(tmp_path,in_process,bad):
    dem=terrain(tmp_path/'dem.tif',missing=bad=='nodata',crs='EPSG:4326' if bad=='geographic' else 'EPSG:32642')
    output=tmp_path/'view.tif'
    coordinates=(500015,4646385) if bad=='edge' else (502715,4646385)
    with pytest.raises(RuntimeError,match='Missing terrain|projected metric|Incomplete DEM'):
        generate_viewshed(dem,output,coordinates,settings=ViewshedSettings(radius_m=2000))
    assert not output.exists()
    assert not output.with_suffix('.tif.json').exists()


def test_failed_replacement_preserves_previous_checkpoint(tmp_path,in_process):
    dem=terrain(tmp_path/'dem.tif')
    output=tmp_path/'view.tif'
    settings=ViewshedSettings(radius_m=2000)
    generate_viewshed(dem,output,(502715,4646385),settings=settings)
    old=output.read_bytes()
    marker=output.with_suffix('.tif.json').read_bytes()
    terrain(dem,missing=True)
    with pytest.raises(RuntimeError,match='Missing terrain'):
        generate_viewshed(dem,output,(502715,4646385),settings=settings)
    assert output.read_bytes()==old
    assert output.with_suffix('.tif.json').read_bytes()==marker


def test_native_timeout_and_disk_reserve(monkeypatch):
    snapshot=native.resource_snapshot()
    healthy={**snapshot,'available_ram_bytes':8*2**30,'available_commit_bytes':8*2**30,'free_disk_bytes':30*2**30}
    monkeypatch.setattr(native,'resource_snapshot',lambda:healthy)
    with pytest.raises(TimeoutError):
        native.run_native([sys.executable,'-c','import time;time.sleep(10)'],timeout=.01,grass=False)
    monkeypatch.setattr(native,'resource_snapshot',lambda:{**snapshot,'free_disk_bytes':0})
    with pytest.raises(RuntimeError,match='free-disk reserve'):
        native.run_native([sys.executable,'-c','import time;time.sleep(10)'],grass=False)


def test_adapter_limits_and_source_protection(tmp_path):
    with pytest.raises(ValueError,match='radius'):
        ViewshedSettings(radius_m=150000).validate()
    dem=tmp_path/'input.tif'
    with pytest.raises(ValueError,match='never an input'):
        generate_viewshed(dem,dem,(0,0))


def test_real_subprocess_adapter_when_resources_allow(tmp_path):
    from beyond_the_summit.runtime import require_resources, config
    cfg=config()
    override=os.environ.get('BTS_TEST_ENTRY_RAM_GIB')
    if override is not None:cfg['resources']['pilot_entry_available_gib']=float(override)
    try:
        require_resources(cfg,pilot=True)
    except RuntimeError as error:
        if override is not None:raise
        pytest.skip(f'Real subprocess integration pending: {error}')
    dem=terrain(tmp_path/'dem.tif',ridge=True)
    report=generate_viewshed(dem,tmp_path/'view.tif',(502715,4646385),settings=ViewshedSettings(radius_m=2000),
                             entry_available_ram_gib=float(override) if override is not None else None)
    assert report['status']=='complete'
    assert sample(tmp_path/'view.tif',504515,4646385)==0


def test_native_ram_and_scratch_safeguards(monkeypatch,tmp_path):
    snapshot=native.resource_snapshot()
    healthy={**snapshot,'available_ram_bytes':8*2**30,'available_commit_bytes':8*2**30,'free_disk_bytes':30*2**30}
    monkeypatch.setattr(native,'resource_snapshot',lambda:healthy)
    with pytest.raises(RuntimeError,match='scratch-space budget'):
        native.run_native([sys.executable,'-c','import time;time.sleep(10)'],grass=False,
                          scratch_directories=(tmp_path,),scratch_limit_bytes=1)
    monkeypatch.setattr(native,'resource_snapshot',lambda:{**healthy,'available_ram_bytes':0})
    with pytest.raises(RuntimeError,match='resource reserve'):
        native.run_native([sys.executable,'-c','import time;time.sleep(10)'],grass=False)
