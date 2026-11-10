"""Standard-library-only pre-deployment integrity check; never runs GIS."""
import hashlib,json
from pathlib import Path
repo=Path(__file__).resolve().parents[3]
site=repo/'docs/day05'
marker=json.loads((site/'bts-export.json').read_text(encoding='utf-8'))
for name,expected in marker['files'].items():
    # Manifests produced on Windows must also verify in Linux Pages runners.
    path=(site/name.replace('\\','/')).resolve()
    if not path.is_relative_to(site.resolve()):raise ValueError('Export path outside site')
    if hashlib.sha256(path.read_bytes()).hexdigest()!=expected:raise ValueError('Modified export: '+name)
print('Verified',len(marker['files']),'G6 static files; existing Days 01–04 preserved.')
gallery=repo/'docs/gallery/export.json'
if gallery.exists():
    manifest=json.loads(gallery.read_text(encoding='utf-8'))
    docs=repo/'docs'
    for name,expected in manifest['files'].items():
        path=(docs/name).resolve()
        if not path.is_relative_to(docs.resolve()):raise ValueError('Gallery path outside docs')
        if hashlib.sha256(path.read_bytes()).hexdigest()!=expected:raise ValueError('Modified gallery file: '+name)
    for name,expected in manifest['sources'].items():
        if name.startswith('docs/day0') and not name.startswith('docs/day05/'):
            if hashlib.sha256((repo/name).read_bytes()).hexdigest()!=expected:raise ValueError('Original report changed: '+name)
    print('Verified',len(manifest['files']),'gallery files and preserved original report images.')
