import json
import pytest
from beyond_the_summit.acquire import download
from beyond_the_summit.runtime import atomic_json


class Response:
    def __init__(self,status,headers,content=b''):
        self.status_code=status;self.headers=headers;self.content=content
    def __enter__(self):return self
    def __exit__(self,*args):pass
    def raise_for_status(self):pass
    def iter_content(self,chunk_size):yield self.content


class Session:
    def __init__(self,resume=True):self.resume=resume;self.headers=None
    def head(self,*args,**kwargs):return Response(200,{'Content-Length':'6','ETag':'object-v1'})
    def get(self,*args,**kwargs):
        self.headers=kwargs['headers']
        return Response(206,{'Content-Range':'bytes 3-5/6'},b'def') if self.resume else Response(200,{},b'abcdef')


@pytest.mark.parametrize('resume',[True,False])
def test_interrupted_download_resumes_or_restarts_if_server_ignores_range(tmp_path,resume):
    url='https://example.test/tile';dest=tmp_path/'tile.tif'
    dest.with_suffix('.tif.partial').write_bytes(b'abc')
    atomic_json(dest.with_suffix('.tif.download.json'),{'url':url,'identity':'object-v1','expected_bytes':6})
    session=Session(resume)
    record=download(url,dest,session=session)
    assert dest.read_bytes()==b'abcdef'
    assert session.headers=={'Range':'bytes=3-','If-Range':'object-v1'}
    assert len(record['sha256'])==64
    assert download(url,dest,session=session)['cache_hit']


def test_over_budget_download_and_unverified_completed_file_are_rejected(tmp_path):
    dest=tmp_path/'tile.tif'
    with pytest.raises(ValueError,match='over-budget'):
        download('https://example.test/tile',dest,session=Session(),maximum_bytes=2)
    dest.write_bytes(b'abcdef')
    with pytest.raises(ValueError,match='unverified'):
        download('https://example.test/tile',dest,session=Session())
