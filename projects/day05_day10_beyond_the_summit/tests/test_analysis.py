import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from beyond_the_summit import analysis,g3_benchmark
from beyond_the_summit.runtime import fingerprint,config


def test_control_changes_preserve_model_signature(tmp_path,monkeypatch):
    monkeypatch.setattr(analysis,'CONTROL',tmp_path/'control.json')
    spec={'analysis':{'radius':100000},'inputs':{'dem':'digest'}}
    before=analysis.specification_key(spec)
    for workers in (3,1,0,2):
        analysis.set_control(workers)
        assert analysis.desired_workers()==workers
        assert analysis.specification_key(spec)==before
    for bad in (-1,4,True,1.5):
        with pytest.raises(ValueError):analysis.set_control(bad)


def test_scheduler_drains_on_reduction_and_resumes_valid_checkpoints(tmp_path,monkeypatch):
    monkeypatch.setattr(analysis,'PROJECT',tmp_path)
    monkeypatch.setattr(g3_benchmark,'PROJECT',tmp_path)
    monkeypatch.setattr(analysis,'CONTROL',tmp_path/'control.json')
    healthy={'available_ram_bytes':8*2**30,'available_commit_bytes':8*2**30,'free_disk_bytes':30*2**30}
    monkeypatch.setattr(analysis,'resource_snapshot',lambda:healthy)
    monkeypatch.setattr(analysis,'native_environment',lambda **k:{})
    monkeypatch.setattr(analysis,'compile_metrics',lambda data:None)
    clock=[0.0];monkeypatch.setattr(analysis.time,'monotonic',lambda:clock[0])
    monkeypatch.setattr(analysis.time,'sleep',lambda seconds:clock.__setitem__(0,clock[0]+seconds))
    events=[]
    class Log:
        id='test'
        def event(self,kind,**values):events.append((kind,values))
    launches=[]
    class Process:
        def __init__(self,args,**kwargs):
            self.request=json.loads(Path(args[-1]).read_text(encoding='utf-8'))
            self.start=clock[0];self.returncode=None;self.pid=90000+len(launches)
            launches.append(self)
            if len(launches)==3:analysis.set_control(1)
        def poll(self):
            if clock[0]-self.start<5:return None
            if self.returncode is None:
                artifact=tmp_path/f'{self.pid}.bin';artifact.write_bytes(b'completed')
                marker=Path(self.request['marker'])
                marker.write_text(json.dumps({'status':'complete','signature':self.request['signature'],
                    'artifact_sha256':{artifact.name:fingerprint(artifact)}}),encoding='utf-8')
                self.returncode=0
            return self.returncode
    monkeypatch.setattr(analysis.subprocess,'Popen',Process)
    analysis.set_control(3)
    observers=[{'observer_id':str(i),'x':0,'y':0} for i in range(6)]
    spec={'analysis':{},'landmarks':{}}
    result=analysis.schedule(observers,spec=spec,phase='production',run=Log())
    assert result['completed']==6 and result['maximum_active_workers']==3
    starts=[values for kind,values in events if kind=='observer_started']
    assert all(s['active']==1 for s in starts[3:])
    before=len(launches)
    replay=analysis.schedule(observers,spec=spec,phase='production',run=Log())
    assert replay['reused_at_start']==6 and len(launches)==before
