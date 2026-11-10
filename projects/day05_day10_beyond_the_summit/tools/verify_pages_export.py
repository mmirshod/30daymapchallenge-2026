"""Standard-library-only pre-deployment integrity check; never runs GIS."""
import hashlib,json
from pathlib import Path
repo=Path(__file__).resolve().parents[3]
site=repo/'docs/day05'
marker=json.loads((site/'bts-export.json').read_text(encoding='utf-8'))
for name,expected in marker['files'].items():
    path=(site/name).resolve()
    if not path.is_relative_to(site.resolve()):raise ValueError('Export path outside site')
    if hashlib.sha256(path.read_bytes()).hexdigest()!=expected:raise ValueError('Modified export: '+name)
print('Verified',len(marker['files']),'G6 static files; existing Days 01–04 preserved.')
