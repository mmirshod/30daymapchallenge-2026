"""Acceptance checks of actual G6 artifacts, not implementation snapshots."""
import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote
import numpy as np
import pytest
from beyond_the_summit.runtime import PROJECT, fingerprint

def exported():
    path=PROJECT/'data/processed/g6_export.json'
    if not path.exists():pytest.skip('G6 not exported yet')
    return json.loads(path.read_text(encoding='utf-8'))

def test_web_scores_reproduce_frozen_rankings():
    exported();data=json.loads((PROJECT/'web/data/explorer.json').read_text(encoding='utf-8'))
    rows=data['summits'];assert len(rows)==1302
    assert len({r['id'] for r in rows})==1302
    for row in rows:
        nps=np.dot(row['components'],[.30,.25,.30,.15])
        assert nps==pytest.approx(row['nps'],abs=1e-10)
        assert .8*nps+.2*row['landmark_score']==pytest.approx(row['mps'],abs=1e-10)
        assert -90<=row['lat']<=90 and -180<=row['lon']<=180
        assert len(row['horizon_visible'])<=15 and row['id'] not in row['horizon_visible']
    assert len(data['landmarks'])==15

def test_every_profile_and_connection_is_valid():
    exported();data=json.loads((PROJECT/'web/data/explorer.json').read_text(encoding='utf-8'))
    n=len(data['targets'])
    for row in data['summits']:
        detail=json.loads((PROJECT/'web/data/details'/(row['id'].replace(':','_')+'.json')).read_text())
        assert len(detail['profile'])==360
        az,angles=np.array(detail['profile']).T
        assert np.isfinite(angles).all() and np.all(np.diff(az)>=0)
        assert len(detail['visible'])==row['visible_peaks']
        assert all(0<=v[0]<n and v[1]>0 for v in detail['visible'])

def test_six_report_pages_and_local_links():
    exported()
    import pymupdf
    for name in ['day05_beyond_the_summit','day10_beyond_the_prompt']:
        with pymupdf.open(PROJECT/'report/g6'/(name+'.pdf')) as doc:
            assert len(doc)==3
            for i,page in enumerate(doc):
                assert page.rect.width>page.rect.height
                assert len(page.get_text())>500
                for block in page.get_text('dict')['blocks']:
                    for line in block.get('lines',[]):
                        for span in line['spans']:
                            assert span['bbox'][0]>=0 and span['bbox'][2]<=page.rect.width-10
                assert (PROJECT/'report/g6'/(name+f'_page_{i+1:02d}.png')).exists()
    class Links(HTMLParser):
        def handle_starttag(self,tag,attrs):
            for name,value in attrs:
                if name not in ['href','src'] or not value:continue
                if value.startswith(('http:','https:','#','../')):continue
                assert (PROJECT/'web'/unquote(value.split('#')[0].split('?')[0])).exists(),value
    Links().feed((PROJECT/'web/index.html').read_text(encoding='utf-8'))

def test_export_manifest_hashes():
    manifest=exported()
    for name,sha in manifest['files'].items():assert fingerprint(PROJECT/name)==sha,name
