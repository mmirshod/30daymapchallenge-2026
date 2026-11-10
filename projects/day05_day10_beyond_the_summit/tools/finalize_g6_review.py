"""Seal fresh browser QA without rebuilding immutable report/site outputs."""
import hashlib,json
from pathlib import Path
p=Path(__file__).resolve().parents[1]
summary_path=p/'data/processed/g6_export.json'
summary=json.loads(summary_path.read_text(encoding='utf-8'))
qa=p/'report/g6/qa'
result=json.loads((qa/'browser_validation.json').read_text())
if result['status']!='passed':raise ValueError('Browser QA must pass')
summary['files']={name:sha for name,sha in summary['files'].items()
    if not any(part.startswith('qa') for part in (p/name).relative_to(p).parts)}
for name,sha in summary['files'].items():
    if hashlib.sha256((p/name).read_bytes()).hexdigest()!=sha:raise ValueError('Changed non-QA output: '+name)
summary['browser_qa']={'checks':len(result['checks']),'status':'passed','max_error':result['score_max_error'],
    'evidence_sha256':hashlib.sha256((qa/'browser_validation.json').read_bytes()).hexdigest()}
summary_path.write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print('Sealed',len(result['checks']),'browser checks; all report/site hashes verified.')
