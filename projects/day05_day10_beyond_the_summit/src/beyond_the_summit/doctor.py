from __future__ import annotations

from datetime import datetime, timezone
import importlib
import importlib.metadata
import platform
import sys

from .native import executable, run_native, grass_command
from .runtime import PROJECT, atomic_json, resource_snapshot


def inspect_environment() -> dict:
    report = {'timestamp_utc': datetime.now(timezone.utc).isoformat(), 'python': sys.version,
              'executable': sys.executable, 'platform': platform.platform(),
              'resources': resource_snapshot(), 'packages': {}, 'native': {}}
    for package in ['geopandas','rasterio','pyogrio','shapely','numpy','scipy','pandas','pyarrow',
                    'networkx','matplotlib','reportlab','jinja2','yaml','typer','pytest','osmium','psutil']:
        try:
            module = importlib.import_module(package)
            report['packages'][package] = {'available': True, 'version': getattr(module, '__version__', None)}
        except Exception as error:
            report['packages'][package] = {'available': False, 'error': str(error)}
    for name, arguments in [('gdalinfo',['--version']),('grass',['--version'])]:
        try:
            path = executable(name)
            result = grass_command(arguments,timeout=60) if name=='grass' else run_native([path,*arguments],timeout=60)
            report['native'][name] = {'available': True, 'path':path, 'version_output':result.stdout.strip()}
        except Exception as error:
            report['native'][name] = {'available':False,'error':str(error)}
    try:
        from osgeo import gdal
        report['gdal_python'] = gdal.VersionInfo('--version')
    except Exception as error:
        report['gdal_python_error'] = str(error)
    report['ready_for_pilot_resources'] = report['resources']['available_ram_bytes'] >= 4*2**30
    atomic_json(PROJECT / 'data/processed/environment.json',report)
    return report

