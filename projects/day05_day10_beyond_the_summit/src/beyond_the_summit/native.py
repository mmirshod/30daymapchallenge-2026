"""Native GIS tools launched without changing the machine environment."""
from __future__ import annotations

import os
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time

import psutil

from .runtime import PROJECT, config, resource_snapshot


def native_environment(*, grass: bool = True) -> dict[str, str]:
    environment = os.environ.copy()
    prefix = Path(sys.prefix)
    environment['PATH'] = os.pathsep.join(str(p) for p in
        [prefix, prefix/'Library/bin', prefix/'Scripts', prefix/'Library/usr/bin']) + os.pathsep + environment.get('PATH', '')
    environment['PYTHONNOUSERSITE'] = '1'
    environment['PYTHONUTF8'] = '1'
    environment['PYTHONIOENCODING'] = 'utf-8'
    environment['GDAL_NUM_THREADS'] = '1'
    environment['GDAL_CACHEMAX'] = '128'
    environment['OMP_NUM_THREADS'] = '1'
    environment['OPENBLAS_NUM_THREADS'] = '1'
    temporary = PROJECT / '.runtime/tmp'
    temporary.mkdir(parents=True, exist_ok=True)
    environment['TEMP'] = environment['TMP'] = str(temporary)
    for name, folder in [('PROJ_DATA', prefix/'Library/share/proj'), ('GDAL_DATA', prefix/'Library/share/gdal')]:
        if folder.exists():
            environment[name] = str(folder)
    bases=sorted((prefix/'Library/lib').glob('grass*'))
    if grass and bases:
        base=bases[-1]
        environment['GISBASE']=str(base)
        environment['GRASS_PYTHON']=sys.executable
        configuration=PROJECT.parents[1]/'.bts/grass-config'
        configuration.mkdir(parents=True,exist_ok=True)
        environment['GRASS_CONFIG_DIR']=str(configuration)
        environment['PYTHONPATH']=str(base/'etc/python')+os.pathsep+environment.get('PYTHONPATH','')
        environment['PATH']=str(base/'bin')+os.pathsep+str(base/'scripts')+os.pathsep+environment['PATH']
        # GRASS conda-forge Windows build expects the MSVC OpenMP DLL filename,
        # while its installed llvm-openmp runtime is named libomp.dll. This
        # package issue is documented in OSGeo/grass#7615. Provide an identical,
        # hashed alias in a GRASS-only search directory, not in System32 or by
        # replacing any package-owned DLL.
        source=prefix/'Library/bin/libomp.dll'
        compatibility=PROJECT.parents[1]/'.bts/grass-compat'
        compatibility.mkdir(parents=True,exist_ok=True)
        alias=compatibility/'libomp140.x86_64.dll'
        if not source.exists():
            raise RuntimeError('GRASS requires the pinned llvm-openmp runtime')
        with source.open('rb') as handle:
            digest=hashlib.file_digest(handle,'sha256').hexdigest()
        if not alias.exists():
            shutil.copyfile(source,alias)
        with alias.open('rb') as handle:
            if hashlib.file_digest(handle,'sha256').hexdigest()!=digest:
                raise RuntimeError('GRASS OpenMP alias differs from installed runtime')
        (compatibility/'manifest.json').write_text(json.dumps({'source':str(source),'alias':str(alias),
            'sha256':digest,'reason':'https://github.com/OSGeo/grass/issues/7615'},indent=2),encoding='utf-8')
        environment['PATH']=str(compatibility)+os.pathsep+environment['PATH']
    return environment


def executable(name: str) -> str:
    environment = native_environment()
    found = shutil.which(name, path=environment['PATH'])
    if found:
        return found
    if name == 'grass':
        prefix = Path(sys.prefix)
        matches = sorted(prefix.glob('Library/grass*/grass*.bat')) + sorted(prefix.glob('Scripts/grass*.bat'))
        if matches:
            return str(matches[-1])
    raise RuntimeError(f'Native executable not available: {name}; use the isolated runtime')


def run_native(arguments: list[str], *, timeout: float = 120, cwd: Path | None = None,
               grass: bool = True, scratch_directories: tuple[Path, ...] = (),
               scratch_limit_bytes: int | None = None) -> subprocess.CompletedProcess:
    # Lists are used throughout; never interpolate user values into a shell command.
    started=time.monotonic();peak_rss=0;minimum_ram=None;low_samples=0;peak_scratch=0;sample=0
    limits=config()['resources'];scratch_root=PROJECT.parents[1]/'.bts/tmp'
    scratch_root.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryFile(dir=scratch_root) as stdout, tempfile.TemporaryFile(dir=scratch_root) as stderr:
        process=subprocess.Popen(arguments,env=native_environment(grass=grass),cwd=cwd or PROJECT,stdout=stdout,stderr=stderr)
        try:
            while process.poll() is None:
                resources=resource_snapshot()
                minimum_ram=min(minimum_ram or resources['available_ram_bytes'],resources['available_ram_bytes'])
                low=(resources['available_ram_bytes']<limits['runtime_reserve_available_gib']*2**30
                     or resources.get('available_commit_bytes',2**63)<limits['runtime_reserve_available_commit_gib']*2**30)
                low_samples=low_samples+1 if low else 0
                if low_samples>=6:raise RuntimeError('Native resource reserve breached for 3 seconds')
                if resources['free_disk_bytes']<limits['free_disk_reserve_gib']*2**30:
                    raise RuntimeError('Native free-disk reserve breached')
                if time.monotonic()-started>timeout:raise TimeoutError('Native command exceeded its time budget')
                if sample%6==0:
                    scratch=0
                    for root in [scratch_root,PROJECT/'.runtime/tmp',PROJECT/'data/interim/pilot',*scratch_directories]:
                        if root.exists():
                            for path in root.rglob('*'):
                                try:
                                    if path.is_file():scratch+=path.stat().st_size
                                except FileNotFoundError:pass
                    peak_scratch=max(peak_scratch,scratch)
                    if scratch>(scratch_limit_bytes if scratch_limit_bytes is not None else limits['pilot_scratch_gib']*2**30):
                        raise RuntimeError('Native scratch-space budget exceeded')
                sample+=1
                try:
                    parent=psutil.Process(process.pid)
                    rss=psutil.Process().memory_info().rss
                    for child in [parent,*parent.children(recursive=True)]:
                        try:rss+=child.memory_info().rss
                        except (psutil.Error,OSError):pass
                    peak_rss=max(peak_rss,rss)
                except psutil.NoSuchProcess:pass
                time.sleep(.5)
        except BaseException:
            try:
                for child in reversed(psutil.Process(process.pid).children(recursive=True)):
                    try:child.terminate()
                    except psutil.Error:pass
            except (psutil.Error,OSError):pass
            if process.poll() is None:
                process.terminate()
                try:process.wait(timeout=10)
                except subprocess.TimeoutExpired:process.kill();process.wait()
            raise
        stdout.seek(0);stderr.seek(0)
        result=subprocess.CompletedProcess(arguments,process.returncode,
            stdout.read().decode('utf-8',errors='replace'),stderr.read().decode('utf-8',errors='replace'))
    result.measurements={'wall_seconds':time.monotonic()-started,'peak_process_tree_rss_bytes':peak_rss,
                         'minimum_available_ram_bytes':minimum_ram,'sampling_interval_seconds':.5,
                         'peak_sampled_scratch_bytes':peak_scratch}
    if result.returncode:
        raise RuntimeError(f'Native command failed ({result.returncode}): {arguments[0]}\n'
                           + result.stderr[-4000:] + '\n' + result.stdout[-2000:])
    return result


def grass_command(arguments: list[str], *, timeout: float = 120) -> subprocess.CompletedProcess:
    # The conda-forge grass.bat unconditionally clears GRASS_CONFIG_DIR. Execute
    # its unmodified Python entrypoint with equivalent GISBASE/path settings so
    # configuration stays inside the workspace instead of roaming AppData.
    entries=sorted((Path(sys.prefix)/'Library/lib').glob('grass*/etc/grass_main.py'))
    if not entries:
        raise RuntimeError('GRASS Python launcher not found in isolated prefix')
    return run_native([sys.executable,str(entries[-1]),*arguments],timeout=timeout)

