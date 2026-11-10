"""Seal fresh browser QA without rebuilding immutable report/site outputs."""
import hashlib,json
from pathlib import Path
p=Path(__file__).resolve().parents[1]
summary_path=p/'data/processed/g6_export.json'
summary=json.loads(summary_path.read_text(encoding='utf-8'))
qa=p/'report/g6/qa'
result=json.loads((qa/'browser_validation.json').read_text())
if result['status']!='passed':raise ValueError('Browser QA must pass')
for name,sha in summary['files'].items():
    if (p/name).is_relative_to(qa):continue
    if hashlib.sha256((p/name).read_bytes()).hexdigest()!=sha:raise ValueError('Changed non-QA output: '+name)
for path in qa.rglob('*'):
    if path.is_file():summary['files'][str(path.relative_to(p))]=hashlib.sha256(path.read_bytes()).hexdigest()
summary['browser_qa']={'checks':len(result['checks']),'status':'passed','max_error':result['score_max_error']}
summary_path.write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print('Sealed',len(result['checks']),'browser checks; all report/site hashes verified.')
