"""Acquire small version-pinned Leaflet assets; Python only, no Node build."""
import hashlib,json,urllib.request
from pathlib import Path
project=Path(__file__).resolve().parents[1]
root=project/'data/raw/publication/vendor';root.mkdir(parents=True,exist_ok=True)
sources={
    'leaflet.js':'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js',
    'leaflet.css':'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css',
    'LICENSE':'https://unpkg.com/leaflet@1.9.4/LICENSE',
    'images/layers.png':'https://unpkg.com/leaflet@1.9.4/dist/images/layers.png',
    'images/layers-2x.png':'https://unpkg.com/leaflet@1.9.4/dist/images/layers-2x.png',
    'images/marker-icon.png':'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
    'images/marker-icon-2x.png':'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
    'images/marker-shadow.png':'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
}
manifest={}
for name,url in sources.items():
    path=root/name;path.parent.mkdir(parents=True,exist_ok=True)
    if not path.exists():
        with urllib.request.urlopen(url,timeout=60) as response:path.write_bytes(response.read())
    manifest[name]={'url':url,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'bytes':path.stat().st_size}
(root/'sources.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print('Leaflet assets ready:',sum(r['bytes'] for r in manifest.values()),'bytes')
