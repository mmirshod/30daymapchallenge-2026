import json
import pytest
from beyond_the_summit import runtime


def test_resource_gate_blocks_low_memory(monkeypatch):
    cfg={'resources':{'pilot_entry_available_gib':4,'runtime_reserve_available_gib':2,'free_disk_reserve_gib':15}}
    monkeypatch.setattr(runtime,'resource_snapshot',lambda:{'available_ram_bytes':3*2**30,'free_disk_bytes':30*2**30})
    with pytest.raises(RuntimeError,match='RAM'):
        runtime.require_resources(cfg,pilot=True)
    runtime.require_resources(cfg,pilot=False)
    with pytest.raises(RuntimeError,match='disk'):
        runtime.require_resources(cfg,additional_disk_bytes=20*2**30)


def test_windows_commit_capacity_blocks_work_even_with_free_ram(monkeypatch):
    cfg={'resources':{'pilot_entry_available_gib':4,'runtime_reserve_available_gib':2,'free_disk_reserve_gib':15}}
    monkeypatch.setattr(runtime,'resource_snapshot',lambda:{'available_ram_bytes':6*2**30,
        'available_commit_bytes':1*2**30,'free_disk_bytes':30*2**30})
    with pytest.raises(RuntimeError,match='commit capacity'):
        runtime.require_resources(cfg,pilot=True)


def test_failed_atomic_write_preserves_valid_artifact(tmp_path):
    p=tmp_path/'result.json'
    runtime.atomic_json(p,{'valid':True})
    with pytest.raises(ValueError):
        runtime.atomic_json(p,{'bad':float('nan')})
    assert json.loads(p.read_text())=={'valid':True}
    assert len(list(tmp_path.iterdir()))==1
