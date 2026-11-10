"""Worker executed only inside an initialized GRASS project."""
from __future__ import annotations

import json
from pathlib import Path
import sys
import time


def main():
    import grass.script as gs
    request=json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
    stages={};started=time.monotonic()
    gs.run_command('r.in.gdal',input=request['dem'],output='terrain',quiet=True)
    stages['import_seconds']=time.monotonic()-started
    gs.run_command('g.region',raster='terrain')
    started=time.monotonic()
    gs.run_command('r.viewshed',input='terrain',output='visibility',
        coordinates=request['coordinates'],observer_elevation=request['observer_height_m'],
        target_elevation=request.get('target_height_m',0),max_distance=request['radius_m'],
        refraction_coeff=request['refraction_coefficient'],memory=request.get('memory_mb',64),
        flags=request.get('flags','bcr'),quiet=True)
    stages['viewshed_seconds']=time.monotonic()-started;started=time.monotonic()
    gs.run_command('r.out.gdal',input='visibility',output=request['output'],format='GTiff',
        type='Byte',nodata=255,createopt='COMPRESS=DEFLATE',quiet=True)
    stages['export_seconds']=time.monotonic()-started
    Path(request['output']).with_suffix('.stages.json').write_text(json.dumps(stages,indent=2),encoding='utf-8')


if __name__=='__main__':
    main()

