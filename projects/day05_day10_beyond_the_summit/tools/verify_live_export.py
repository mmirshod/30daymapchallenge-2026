"""Verify published assets against the reviewed local export, without credentials."""
import argparse,datetime,hashlib,json,urllib.request
from pathlib import Path
parser=argparse.ArgumentParser();parser.add_argument('--sha',required=True)
args=parser.parse_args()
p=Path(__file__).resolve().parents[1];repo=p.parents[1]
site=repo/'docs/day05';manifest=json.loads((site/'bts-export.json').read_text())
expected={k.replace('\\','/'):v for k,v in manifest['files'].items()}
base='https://mmirshod.github.io/30daymapchallenge-2026/'
names=['index.html','app.js','i18n.js','scores.js','style.css','terrain.png','data/explorer.json',
    'data/details/node_2556670543.json','data/details/node_1544318728.json',
    'downloads/day05_beyond_the_summit.pdf','downloads/day10_beyond_the_prompt.pdf','downloads/rankings.csv']
results=[]
for name in names:
    url=base+'day05/'+name+'?release='+args.sha
    with urllib.request.urlopen(url,timeout=60) as response:
        data=response.read();status=response.status;content_type=response.headers.get('Content-Type')
    sha=hashlib.sha256(data).hexdigest()
    if status!=200 or sha!=expected[name]:raise ValueError('Published asset mismatch: '+name)
    if name.endswith('.pdf') and not data.startswith(b'%PDF-'):raise ValueError('Not a PDF: '+name)
    results.append({'path':name,'status':status,'bytes':len(data),'sha256':sha,'content_type':content_type})
for name in ['index.html','day01/index.html']:
    with urllib.request.urlopen(base+name+'?release='+args.sha,timeout=60) as response:
        assert response.status==200
        results.append({'path':name,'status':response.status,'bytes':len(response.read())})
result={'status':'passed','commit':args.sha,'verified_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'url':base+'day05/','assets':results}
output=p/'report/g6/qa_live';output.mkdir(parents=True,exist_ok=True)
(output/'http_validation.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print('Verified live export:',len(results),'HTTP assets including both PDF hashes and existing Day 01.')
