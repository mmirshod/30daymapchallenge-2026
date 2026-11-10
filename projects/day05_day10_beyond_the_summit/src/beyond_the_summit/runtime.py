"""Configuration, immutable fingerprints, atomic artifacts and honest telemetry."""
from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import ctypes
import json
import os
from pathlib import Path
import threading
import time
import uuid

import psutil
import yaml

PROJECT = Path(__file__).resolve().parents[2]
REPOSITORY = PROJECT.parents[1]


def config(path: Path | None = None) -> dict:
    with (path or PROJECT / 'config/analysis.yaml').open(encoding='utf-8') as handle:
        return yaml.safe_load(handle)


def fingerprint(path: Path) -> str:
    with path.open('rb') as handle:
        return hashlib.file_digest(handle, 'sha256').hexdigest()


def atomic_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + '.' + uuid.uuid4().hex + '.partial')
    try:
        with temporary.open('w', encoding='utf-8', newline='\n') as handle:
            json.dump(value, handle, indent=2, ensure_ascii=False, allow_nan=False, default=str)
            handle.write('\n')
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def resource_snapshot() -> dict:
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage(str(PROJECT))
    snapshot={'available_ram_bytes': memory.available, 'total_ram_bytes': memory.total,
              'free_disk_bytes': disk.free, 'total_disk_bytes': disk.total}
    if os.name=='nt':
        class MemoryStatus(ctypes.Structure):
            _fields_=[('length',ctypes.c_ulong),('load',ctypes.c_ulong)]+[(name,ctypes.c_ulonglong)
                for name in ['total_phys','avail_phys','total_page','avail_page','total_virtual','avail_virtual','extended']]
        status=MemoryStatus();status.length=ctypes.sizeof(status)
        if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
            snapshot.update(commit_limit_bytes=status.total_page,available_commit_bytes=status.avail_page)
    return snapshot


def require_resources(cfg: dict, *, pilot: bool = False, additional_disk_bytes: int = 0) -> dict:
    snapshot = resource_snapshot()
    limits = cfg['resources']
    required_ram = limits['pilot_entry_available_gib'] if pilot else limits['runtime_reserve_available_gib']
    reasons = []
    if snapshot['available_ram_bytes'] < required_ram * 2**30:
        reasons.append(f"available RAM {snapshot['available_ram_bytes']/2**30:.2f} GiB < {required_ram} GiB")
    required_commit=limits.get('pilot_entry_available_commit_gib' if pilot else 'runtime_reserve_available_commit_gib',required_ram)
    if snapshot.get('available_commit_bytes',snapshot['available_ram_bytes']) < required_commit*2**30:
        reasons.append(f'available virtual-memory commit capacity < {required_commit} GiB')
    if snapshot['free_disk_bytes'] - additional_disk_bytes < limits['free_disk_reserve_gib'] * 2**30:
        reasons.append('insufficient disk after planned work and reserve')
    if reasons:
        raise RuntimeError('Resource gate: ' + '; '.join(reasons))
    return snapshot


class Run:
    def __init__(self, stage: str, parameters: dict | None = None):
        self.id = uuid.uuid4().hex
        self.stage = stage
        self.path = PROJECT / 'logs/runs' / f'{self.id}.jsonl'
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.parameters = parameters or {}
        self.stop = threading.Event()
        self.peak_rss = 0
        self.minimum_available_ram: int | None = None
        self.telemetry_errors: set[str] = set()
        self._thread: threading.Thread | None = None

    def event(self, kind: str, **fields) -> None:
        event = {'run_id': self.id, 'stage': self.stage, 'event': kind, 'actor': 'codex',
                 'timestamp_utc': datetime.now(timezone.utc).isoformat(), **fields}
        with self.path.open('a', encoding='utf-8', newline='\n') as output:
            output.write(json.dumps(event, ensure_ascii=False, allow_nan=False, default=str) + '\n')

    def _sample(self) -> None:
        process = psutil.Process()
        while not self.stop.is_set():
            rss = 0
            try:
                processes=[process,*process.children(recursive=True)]
            except (psutil.Error,OSError) as error:
                self.telemetry_errors.add(f'process-tree enumeration: {type(error).__name__}: {error}')
                processes=[process]
            for p in processes:
                try:
                    rss += p.memory_info().rss
                except (psutil.Error,OSError) as error:
                    self.telemetry_errors.add(f'process memory: {type(error).__name__}: {error}')
            available = psutil.virtual_memory().available
            self.peak_rss = max(self.peak_rss, rss)
            self.minimum_available_ram = min(self.minimum_available_ram or available, available)
            self.stop.wait(0.25)

    @contextmanager
    def capture(self):
        started = time.monotonic()
        self.event('start', parameters=self.parameters, resources=resource_snapshot(),
                   config_sha256=fingerprint(PROJECT / 'config/analysis.yaml'))
        self._thread = threading.Thread(target=self._sample, daemon=True)
        self._thread.start()
        result = 'success'
        try:
            yield self
        except BaseException as error:
            result = 'failure'
            self.event('error', error_type=type(error).__name__, message=str(error))
            raise
        finally:
            self.stop.set()
            self._thread.join(timeout=2)
            self.event('finish', status=result, wall_seconds=time.monotonic()-started,
                       peak_process_tree_rss_bytes=self.peak_rss,
                       minimum_available_ram_bytes=self.minimum_available_ram,
                       telemetry_errors=sorted(self.telemetry_errors),
                       resources=resource_snapshot())

