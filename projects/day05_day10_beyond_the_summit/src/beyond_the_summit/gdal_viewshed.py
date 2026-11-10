"""Isolated GDAL terrain viewsheds; the manifest is the completion marker."""
from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
import math
from pathlib import Path
import sys
import tempfile
import time

from osgeo import gdal

from .native import run_native
from .runtime import PROJECT, Run, atomic_json, config, fingerprint, require_resources


@dataclass(frozen=True)
class ViewshedSettings:
    radius_m: float = 100000
    observer_height_m: float = 1.7
    refraction_coefficient: float = 0.14286
    earth_curvature: bool = True
    cache_mb: int = 128
    timeout_seconds: float = 120
    scratch_limit_bytes: int = 8 * 2**30

    def validate(self):
        for value in (self.radius_m, self.observer_height_m, self.refraction_coefficient,
                      self.timeout_seconds, self.cache_mb, self.scratch_limit_bytes):
            if not math.isfinite(value):
                raise ValueError('Viewshed settings must be finite')
        if not 0 < self.radius_m <= 100000 or self.observer_height_m < 0:
            raise ValueError('Require radius in (0, 100 km] and nonnegative observer height')
        if not 0 <= self.refraction_coefficient < 1:
            raise ValueError('Refraction coefficient must be in [0, 1)')
        if self.timeout_seconds <= 0 or self.cache_mb <= 0 or self.scratch_limit_bytes <= 0:
            raise ValueError('Resource limits must be positive')


def generate_viewshed(dem: Path, output: Path, coordinates: tuple[float, float], *,
                      settings: ViewshedSettings | None = None,
                      entry_available_ram_gib: float | None = None) -> dict:
    """Generate Byte 0/1 visibility, 255 outside exact projected-radius mask.

    Input elevations must be metres. Outputs are restricted to the new project
    or workspace temporary tree. Existing prior-day inputs are never modified.
    Reuse requires matching input/config/algorithm/version and output hashes.
    """
    settings = settings or ViewshedSettings()
    settings.validate()
    if len(coordinates) != 2 or not all(math.isfinite(v) for v in coordinates):
        raise ValueError('Observer coordinates must be two finite numbers')
    dem, output = Path(dem).resolve(), Path(output).resolve()
    permitted = (PROJECT.resolve(), (PROJECT.parents[1]/'.bts/tmp').resolve())
    if dem == output or not any(output.is_relative_to(root) for root in permitted):
        raise ValueError('Output must be a new-project artifact, never an input or prior-day file')
    cfg = config()
    if entry_available_ram_gib is not None:
        if (not math.isfinite(entry_available_ram_gib)
                or entry_available_ram_gib < cfg['resources']['runtime_reserve_available_gib']):
            raise ValueError('Entry override must retain the runtime RAM reserve')
        cfg['resources']['pilot_entry_available_gib'] = entry_available_ram_gib
    require_resources(cfg, pilot=True)
    algorithm = {name: fingerprint(Path(__file__).with_name(name))
                 for name in ('gdal_viewshed.py', 'gdal_worker.py', 'native.py', 'runtime.py')}
    lock = PROJECT/'environment-win-64.lock.txt'
    specification = {'dem': str(dem), 'dem_sha256': fingerprint(dem),
                     'coordinates': list(coordinates), 'settings': asdict(settings),
                     'gdal_version': gdal.VersionInfo(), 'algorithm': algorithm,
                     'config_sha256': fingerprint(PROJECT/'config/analysis.yaml'),
                     'environment_sha256': fingerprint(lock),
                     'mode': 'GVM_Edge', 'target_height_m': 0.0}
    signature = hashlib.sha256(json.dumps(specification, sort_keys=True).encode()).hexdigest()
    manifest = output.with_suffix(output.suffix+'.json')
    if manifest.exists() and output.exists():
        try:
            saved = json.loads(manifest.read_text(encoding='utf-8'))
            if (saved['signature'] == signature and saved['status'] == 'complete'
                    and saved['output_sha256'] == fingerprint(output)):
                return {**saved, 'reused': True}
        except (ValueError, KeyError):
            pass  # An interrupted/corrupt marker never counts as a checkpoint.
    output.parent.mkdir(parents=True, exist_ok=True)
    root = PROJECT/'data/interim/gdal_scratch'
    root.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    with tempfile.TemporaryDirectory(prefix='observer_', dir=root) as folder:
        work = Path(folder)
        request = {**specification, 'work': str(work)}
        request_path = work/'request.json'
        atomic_json(request_path, request)
        bootstrap = ("import os,runpy,sys; "
                     "_dll=os.add_dll_directory(os.path.join(sys.prefix,'Library','bin')) if os.name=='nt' else None; "
                     "runpy.run_module('beyond_the_summit.gdal_worker',run_name='__main__')")
        with Run('gdal-observer', {'signature':signature,'coordinates':list(coordinates),
                                  'output':str(output),
                                  'entry_available_ram_gib':cfg['resources']['pilot_entry_available_gib']}).capture() as run:
            native = run_native([sys.executable, '-c', bootstrap, str(request_path)],
                                timeout=settings.timeout_seconds, grass=False,
                                scratch_directories=(root,), scratch_limit_bytes=settings.scratch_limit_bytes)
            run.event('worker_complete',measurements=native.measurements)
        product = work/'viewshed.tif'
        details = json.loads((work/'result.json').read_text(encoding='utf-8'))
        # Reject inputs changed during execution; never publish stale provenance.
        if fingerprint(dem) != specification['dem_sha256']:
            raise RuntimeError('Input DEM changed during viewshed generation')
        digest = fingerprint(product)
        import os
        os.replace(product, output)
        result = {'status': 'complete', 'signature': signature, 'specification': specification,
                  'output': str(output), 'output_sha256': digest, 'reused': False,
                  'measurements': native.measurements, 'details': details, 'run_id':run.id,
                  'adapter_wall_seconds': time.monotonic()-started,
                  'quality': 'exploratory raster-ground visibility; not independently verified sight'}
        atomic_json(manifest, result)
        return result
