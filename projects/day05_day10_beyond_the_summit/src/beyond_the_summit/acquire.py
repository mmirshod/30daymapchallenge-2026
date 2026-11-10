"""Documented, resumable acquisition of missing Copernicus tiles only."""
from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import time

import requests

from .runtime import PROJECT, Run, atomic_json, config, fingerprint, require_resources


def download(url: str, destination: Path, *, session=None, maximum_bytes: int=150*2**20) -> dict:
    """Resume only when remote identity is known and unchanged.

    Completed files are reusable only if recorded URL, size, hash and remote
    identity match. A hash is a local integrity record, not a publisher checksum.
    """
    if not url.startswith('https://'):
        raise ValueError('Acquisition requires HTTPS')
    session=session or requests.Session()
    destination.parent.mkdir(parents=True,exist_ok=True)
    partial=destination.with_suffix(destination.suffix+'.partial')
    metadata=destination.with_suffix(destination.suffix+'.download.json')
    with session.head(url,allow_redirects=True,timeout=(15,60)) as response:
        response.raise_for_status()
        size=int(response.headers.get('Content-Length',0))
        identity=response.headers.get('ETag') or response.headers.get('Last-Modified')
    if size<=0 or size>maximum_bytes:
        raise ValueError(f'Missing/over-budget source length: {size}')
    prior=json.loads(metadata.read_text(encoding='utf-8')) if metadata.exists() else {}
    unchanged=bool(identity) and all(prior.get(k)==v for k,v in {'url':url,'identity':identity,'expected_bytes':size}.items())
    if destination.exists():
        if unchanged and destination.stat().st_size==size and prior.get('sha256')==fingerprint(destination):
            return {**prior,'cache_hit':True}
        raise ValueError(f'Existing completed file has unverified or changed identity: {destination.name}')
    if partial.exists() and (not unchanged or partial.stat().st_size>size):
        # Only the explicitly named in-project partial output is reset.
        partial.unlink()
    record={'url':url,'identity':identity,'expected_bytes':size,'retrieved_utc':datetime.now(timezone.utc).isoformat(),
            'license_source':'https://registry.opendata.aws/copernicus-dem/'}
    atomic_json(metadata,record)
    for attempt in range(3):
        offset=partial.stat().st_size if partial.exists() else 0
        if offset==size:
            break
        headers={'Range':f'bytes={offset}-','If-Range':identity} if offset and identity else {}
        try:
            with session.get(url,headers=headers,stream=True,timeout=(15,60)) as response:
                response.raise_for_status()
                if offset and response.status_code==206:
                    expected=f'bytes {offset}-'
                    if not response.headers.get('Content-Range','').startswith(expected):
                        raise ValueError('Server returned an incorrect resume range')
                    mode='ab'
                elif response.status_code==200:
                    mode='wb';offset=0
                else:
                    raise ValueError(f'Unexpected download status {response.status_code}')
                total=offset
                with partial.open(mode) as output:
                    for chunk in response.iter_content(chunk_size=1024*1024):
                        if not chunk:continue
                        total+=len(chunk)
                        if total>size:
                            raise ValueError('Server returned more bytes than declared')
                        output.write(chunk)
            if partial.stat().st_size!=size:
                raise requests.ConnectionError('Incomplete download')
            break
        except requests.RequestException:
            if attempt==2:raise
            time.sleep(2**attempt)
    if not partial.exists() or partial.stat().st_size!=size:
        raise ValueError('Download did not complete')
    record.update(sha256=fingerprint(partial),cache_hit=False)
    partial.replace(destination)
    atomic_json(metadata,record)
    return record


def acquire_dem(run: Run, *, execute: bool=False, radius_m: int=100000) -> dict:
    path=PROJECT/'data/processed/source_manifest.json'
    if not path.exists():
        raise RuntimeError('Run prepare before acquisition')
    manifest=json.loads(path.read_text(encoding='utf-8'))
    domain=next((d for d in manifest['domains'] if d['radius_m']==radius_m),None)
    if domain is None:raise ValueError('Radius not in prepared scenarios')
    missing=[t for t in domain['tiles'] if t['cached_path'] is None]
    plan={'radius_m':radius_m,'missing_tile_count':len(missing),'tiles':missing,'executed':False,
          'budget_ceiling_bytes':len(missing)*150*2**20,
          'note':'Coverage requires raster validation; remote tile availability is not assumed.'}
    atomic_json(PROJECT/'data/processed/acquisition_plan.json',plan)
    if not execute:return plan
    require_resources(config(),additional_disk_bytes=plan['budget_ceiling_bytes'])
    results=[]
    with requests.Session() as session:
        for tile in missing:
            require_resources(config(),additional_disk_bytes=150*2**20)
            output=PROJECT/'data/raw/dem'/f"{tile['id']}.tif"
            result=download(tile['url'],output,session=session)
            run.event('download',tile_id=tile['id'],**result)
            results.append({'tile_id':tile['id'],**result})
    plan.update(executed=True,results=results)
    atomic_json(PROJECT/'data/processed/acquisition_plan.json',plan)
    return plan

