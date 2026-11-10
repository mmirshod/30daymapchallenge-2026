"""Project-local, no-admin micromamba bootstrap; never changes shell profiles.

Use the existing Python 3.12 to run this script, then use micromamba run for
the fully isolated environment. Only precompiled conda-forge packages are used.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tarfile
import time
from urllib.request import urlopen

PROJECT = Path(__file__).resolve().parents[1]
RUNTIME = PROJECT.parents[1] / '.bts'
MICROMAMBA_VERSION = '2.5.0'


def fetch(url: str, path: Path) -> None:
    temporary = path.with_suffix(path.suffix + '.partial')
    with urlopen(url, timeout=90) as response, temporary.open('wb') as output:
        shutil.copyfileobj(response, output, 1024 * 1024)
    temporary.replace(path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--install', action='store_true')
    args = parser.parse_args()
    RUNTIME.mkdir(parents=True, exist_ok=True)
    logs = PROJECT / 'logs' / 'runs'
    logs.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    log = logs / f'{stamp}_bootstrap.json'
    record = {'started_utc': datetime.now(timezone.utc).isoformat(),
              'actor': 'codex', 'stage': 'bootstrap', 'install_requested': args.install}
    started = time.monotonic()
    try:
        executable = RUNTIME / 'micromamba.exe'
        if not executable.exists():
            metadata = RUNTIME / 'micromamba_metadata.json'
            fetch('https://api.anaconda.org/package/conda-forge/micromamba', metadata)
            info = json.loads(metadata.read_text(encoding='utf-8'))
            files = [f for f in info['files'] if f['version'] == MICROMAMBA_VERSION
                     and f['basename'].startswith('win-64/') and f['basename'].endswith('.tar.bz2')]
            if not files:
                raise RuntimeError('No official win-64 tar.bz2 micromamba package found')
            selected = sorted(files, key=lambda f: f.get('upload_time', ''))[-1]
            url = selected['download_url']
            if url.startswith('//'):
                url = 'https:' + url
            archive = RUNTIME / 'micromamba.tar.bz2'
            fetch(url, archive)
            with archive.open('rb') as handle:
                actual = hashlib.file_digest(handle, 'sha256').hexdigest()
            expected = selected.get('sha256')
            if not expected or actual != expected:
                raise RuntimeError('Micromamba checksum absent or mismatched')
            with tarfile.open(archive, 'r:bz2') as package:
                source = package.extractfile('Library/bin/micromamba.exe')
                if source is None:
                    raise RuntimeError('Executable absent from official archive')
                with source, executable.open('wb') as output:
                    shutil.copyfileobj(source, output)
            (RUNTIME / 'bootstrap_source.json').write_text(json.dumps(
                {'url': url, 'sha256': actual, 'version': selected['version'],
                 'retrieved_utc': datetime.now(timezone.utc).isoformat()}, indent=2), encoding='utf-8')
        environment = os.environ.copy()
        environment['MAMBA_ROOT_PREFIX'] = str(RUNTIME / 'mamba')
        environment['MAMBA_NO_BANNER'] = '1'
        environment['PYTHONNOUSERSITE'] = '1'
        environment['PYTHONUTF8'] = '1'
        environment['MAMBA_DOWNLOAD_THREADS'] = '2'
        environment['MAMBA_EXTRACT_THREADS'] = '1'
        environment['TEMP'] = environment['TMP'] = str(RUNTIME / 'tmp')
        (RUNTIME / 'tmp').mkdir(exist_ok=True)
        specification = PROJECT / 'environment.yml'
        if args.install:
            specification = PROJECT / 'environment-win-64.lock.txt'
            if not specification.exists():
                raise RuntimeError('Inspect a successful dry-run and generate the explicit lock first')
        command = [str(executable), '--no-rc', 'create', '--root-prefix', str(RUNTIME / 'mamba'),
                   '--prefix', str(RUNTIME / 'env'), '--override-channels', '-c', 'conda-forge',
                   '--strict-channel-priority', '--file', str(specification), '--json', '--yes',
                   '--no-shortcuts', '--no-pyc']
        if not args.install:
            command.append('--dry-run')
        record['command'] = command
        result_path = logs / f'{stamp}_mamba_result.json'
        errors_path = logs / f'{stamp}_mamba_stderr.txt'
        with result_path.open('wb') as stdout, errors_path.open('wb') as stderr:
            process = subprocess.Popen(command, env=environment, stdout=stdout, stderr=stderr)
            # Resource monitoring is optional only for bootstrapping from a clean
            # Python; this repository's bootstrap interpreter provides psutil.
            try:
                import psutil
            except ImportError:
                psutil = None
            low_memory_samples = 0
            peak_rss = 0
            while process.poll() is None:
                if time.monotonic() - started > 1800:
                    process.terminate(); process.wait(timeout=30)
                    raise TimeoutError('Environment setup exceeded 30 minutes')
                if psutil is not None:
                    available = psutil.virtual_memory().available
                    try:
                        peak_rss = max(peak_rss, psutil.Process(process.pid).memory_info().rss)
                    except psutil.NoSuchProcess:
                        pass
                    low_memory_samples = low_memory_samples+1 if available < 256*2**20 else 0
                    if low_memory_samples >= 10:
                        process.terminate(); process.wait(timeout=30)
                        raise RuntimeError('Installer stopped after sustained available RAM below 256 MiB')
                time.sleep(1)
        record.update(exit_code=process.returncode, result=str(result_path), stderr=str(errors_path),
                      peak_installer_rss_bytes=peak_rss)
        print(json.dumps(record, indent=2))
        if process.returncode:
            raise RuntimeError(f'Micromamba failed; see {errors_path.name} and {result_path.name}')
    except Exception as error:
        record.update(status='failed', error=f'{type(error).__name__}: {error}')
        raise
    else:
        record['status'] = 'success'
    finally:
        record['duration_s'] = time.monotonic() - started
        record['finished_utc'] = datetime.now(timezone.utc).isoformat()
        log.write_text(json.dumps(record, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()

