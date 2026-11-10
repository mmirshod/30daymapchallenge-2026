"""Checkpointed G4 scheduler with live concurrency control and bounded retries."""
from __future__ import annotations

from collections import deque
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import uuid

import geopandas as gpd
import numpy as np
import pandas as pd
import psutil

from .data_readiness import DEM,write_parquet
from .g3_benchmark import checkpoint_valid
from .native import native_environment
from .runtime import PROJECT,Run,atomic_json,config,fingerprint,require_resources,resource_snapshot

CONTROL=PROJECT/'config/analysis_control.json'
STATUS=PROJECT/'data/processed/g4_status.json'


def set_control(workers):
    if type(workers) is not int or not 0<=workers<=3:raise ValueError('Workers must be 0 (drain/pause), 1, 2 or 3')
    value={'workers':workers,'policy':'drain active observers when reducing; checkpoints remain valid'}
    atomic_json(CONTROL,value)
    return value


def desired_workers(path=None):
    path=path or CONTROL
    value=json.loads(path.read_text(encoding='utf-8'))['workers']
    if type(value) is not int or not 0<=value<=3:raise ValueError('Invalid live worker count')
    return value


def model_specification():
    cfg=config()
    return {'analysis':cfg['analysis'],'landmarks':cfg['landmarks'],
        'inputs':{name:fingerprint(PROJECT/name) for name in ['data/interim/pilot_dem_30m.tif',
            'data/processed/observers.parquet','data/processed/target_peaks.parquet','data/processed/landmarks_audited.parquet']},
        'environment':fingerprint(PROJECT/'environment-win-64.lock.txt'),
        'algorithms':{name:fingerprint(Path(__file__).with_name(name)) for name in
            ['analysis_worker.py','panorama.py','gdal_viewshed.py','gdal_worker.py','g3_benchmark.py','native.py','runtime.py','los.py']},
        'note':'Resource limits, worker count and approval flags do not change the model signature.'}


def specification_key(spec):
    return hashlib.sha256(json.dumps(spec,sort_keys=True).encode()).hexdigest()


def observer_records():
    frame=gpd.read_parquet(PROJECT/'data/processed/observers.parquet')
    if len(frame)!=1302 or frame.observer_id.nunique()!=1302:raise ValueError('Approved cohort changed')
    return [{'observer_id':str(r.observer_id),'x':float(r.geometry.x),'y':float(r.geometry.y),
             'elevation_m':float(r.elevation_m)} for r in frame.sort_values('observer_id').itertuples()]


def _stop_tree(process):
    try:
        for child in reversed(psutil.Process(process.pid).children(recursive=True)):
            try:child.terminate()
            except psutil.Error:pass
    except psutil.Error:pass
    if process.poll() is None:
        process.terminate()
        try:process.wait(timeout=5)
        except subprocess.TimeoutExpired:process.kill();process.wait()


def schedule(observers,*,spec,phase,run,workers=3,maximum_seconds=None):
    cfg=config();signature=specification_key(spec)
    base=PROJECT/'data/interim/g4'/signature[:16];base.mkdir(parents=True,exist_ok=True)
    checkpoints=PROJECT/'data/processed/g4'/signature[:16]/'cases';checkpoints.mkdir(parents=True,exist_ok=True)
    logs=PROJECT/'logs/analysis'/run.id;logs.mkdir(parents=True,exist_ok=True)
    report=PROJECT/f'data/processed/{"g4_parallel_benchmark" if phase=="benchmark" else "g4_status"}.json'
    pending=deque();complete={};failures={};attempts={};active={}
    for observer in observers:
        marker=checkpoints/(observer['observer_id'].replace(':','_')+'.json')
        if checkpoint_valid(marker,signature):complete[observer['observer_id']]=str(marker.relative_to(PROJECT))
        else:pending.append(observer)
    reused=len(complete);started=time.monotonic();last_write=last_launch=0
    minimum_ram=None;peak_rss=0;telemetry_errors=set();resource_events=0;max_active=0
    # Locks prevent two controllers writing the same cohort/checkpoints concurrently.
    lock=base/'scheduler.lock'
    try:
        fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY)
    except FileExistsError:
        owner=json.loads(lock.read_text(encoding='utf-8'))
        if psutil.pid_exists(owner['pid']):raise RuntimeError('An analysis scheduler already owns this model')
        lock.unlink();fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY)
    with os.fdopen(fd,'w',encoding='utf-8') as output:json.dump({'pid':os.getpid(),'run_id':run.id},output)
    bootstrap=("import os,runpy,sys; _dll=os.add_dll_directory(os.path.join(sys.prefix,'Library','bin')) if os.name=='nt' else None; "
               "runpy.run_module('beyond_the_summit.analysis_worker',run_name='__main__')")
    def snapshot(state):
        data={'state':state,'phase':phase,'run_id':run.id,'pid':os.getpid(),'signature':signature,
            'total':len(observers),'completed':len(complete),'reused_at_start':reused,'failed':len(failures),
            'pending':len(pending),'active_observer_ids':list(active),'requested_workers':requested,
            'effective_active_workers':len(active),'wall_seconds':time.monotonic()-started,
            'maximum_active_workers':max_active,
            'minimum_available_ram_bytes':minimum_ram,'sampled_peak_process_tree_rss_bytes':peak_rss,
            'telemetry_errors':sorted(telemetry_errors),'resource_events':resource_events,
            'failures':failures,'completed_checkpoints':complete,'checkpoint_directory':str(checkpoints.relative_to(PROJECT)),
            'live_control_file':str(CONTROL.relative_to(PROJECT)),'production_approved':phase=='production',
            'last_resources':resource_snapshot(),'model_specification':spec}
        atomic_json(report,data)
        return data
    requested=workers
    try:
        while pending or active:
            if maximum_seconds and time.monotonic()-started>maximum_seconds:
                raise TimeoutError('Analysis benchmark exceeded time budget')
            # Atomic control changes only affect scheduling, never fingerprints.
            try:requested=desired_workers() if phase=='production' else workers
            except (OSError,ValueError,KeyError) as error:
                requested=0;run.event('invalid_control_paused',message=str(error))
            resources=resource_snapshot()
            minimum_ram=min(minimum_ram or resources['available_ram_bytes'],resources['available_ram_bytes'])
            try:
                parent=psutil.Process();rss=parent.memory_info().rss
                for child in parent.children(recursive=True):
                    try:rss+=child.memory_info().rss
                    except (psutil.Error,OSError):pass
                peak_rss=max(peak_rss,rss)
            except (psutil.Error,OSError) as error:telemetry_errors.add(str(error))
            for oid,item in list(active.items()):
                process,observer,marker,out,err,launched=item
                code=process.poll()
                if code is None:
                    if time.monotonic()-launched>600:
                        _stop_tree(process);code=process.returncode
                    else:continue
                out.close();err.close();del active[oid]
                if code==0 and checkpoint_valid(marker,signature):
                    complete[oid]=str(marker.relative_to(PROJECT))
                    run.event('observer_complete',observer_id=oid,completed=len(complete),total=len(observers))
                    print(f'{phase}: {len(complete)}/{len(observers)} complete ({oid})',flush=True)
                else:
                    error=Path(err.name).read_text(encoding='utf-8',errors='replace')[-3500:]
                    if attempts[oid]<3:
                        pending.appendleft(observer);run.event('observer_retry',observer_id=oid,error=error)
                    else:
                        failures[oid]={'attempts':attempts[oid],'error':error,'stderr':str(Path(err.name).relative_to(PROJECT))}
            low=(resources['available_ram_bytes']<cfg['resources']['runtime_reserve_available_gib']*2**30
                or resources.get('available_commit_bytes',0)<cfg['resources']['runtime_reserve_available_commit_gib']*2**30
                or resources['free_disk_bytes']<cfg['resources']['free_disk_reserve_gib']*2**30)
            if low:
                resource_events+=1
                # Stop only one owned observer at a time under actual reserve breach.
                # Its incomplete products are ignored; validated stage files survive.
                if active:
                    oid=next(reversed(active));_stop_tree(active[oid][0])
                    run.event('resource_worker_stopped',observer_id=oid,resources=resources)
                if phase=='production' and requested>1:set_control(1);requested=1
            # Leave room for the next worker's measured ~0.5 GiB footprint.
            headroom=resources['available_ram_bytes']>=(cfg['resources']['runtime_reserve_available_gib']+.55)*2**30
            if pending and not low and headroom and len(active)<requested and time.monotonic()-last_launch>=1:
                observer=pending.popleft();oid=observer['observer_id'];name=oid.replace(':','_')
                marker=checkpoints/(name+'.json');attempts[oid]=attempts.get(oid,0)+1
                request=logs/f'{name}.{attempts[oid]}.request.json'
                atomic_json(request,{'observer':observer,'signature':signature,'directory':str(base),
                    'marker':str(marker),'analysis':spec['analysis'],'landmarks':spec['landmarks']})
                out=(logs/f'{name}.{attempts[oid]}.stdout.log').open('wb')
                err=(logs/f'{name}.{attempts[oid]}.stderr.log').open('wb')
                process=subprocess.Popen([sys.executable,'-c',bootstrap,str(request)],env=native_environment(grass=False),
                    cwd=PROJECT,stdout=out,stderr=err)
                active[oid]=(process,observer,marker,out,err,time.monotonic());last_launch=time.monotonic()
                max_active=max(max_active,len(active))
                run.event('observer_started',observer_id=oid,pid=process.pid,active=len(active),requested=requested)
            if time.monotonic()-last_write>=2:
                snapshot('paused' if requested==0 and not active else 'waiting_for_resources' if low or (pending and not active and not headroom) else 'running')
                last_write=time.monotonic()
            time.sleep(.25)
        result=snapshot('complete' if len(complete)==len(observers) else 'complete_with_failures')
        if phase=='production':compile_metrics(result)
        return result
    except BaseException:
        for process,_,_,out,err,_ in active.values():_stop_tree(process);out.close();err.close()
        snapshot('interrupted');raise
    finally:
        lock.unlink(missing_ok=True)


def compile_metrics(status):
    rows=[]
    for oid,path in status['completed_checkpoints'].items():
        c=json.loads((PROJECT/path).read_text(encoding='utf-8'))
        rows.append({'observer_id':oid,'elevation_m':c['observer']['elevation_m'],
            'visible_area_km2':c['terrain']['visible_area_km2'],
            'visible_peak_ground_proxies':c['peaks']['visible_peak_ground_proxies'],
            'unknown_peak_targets':c['peaks']['unknown_targets'],**c['skyline_diagnostics'],
            'lake_visibility_in_ranking':False,'nps':None,'mps':None,'checkpoint':path})
    write_parquet(pd.DataFrame(rows),PROJECT/'data/processed/g4_observer_metrics.parquet')


def parallel_benchmark(run):
    from .validation import validate_artifacts
    if not validate_artifacts().get('g2',{}).get('nps_data_ready'):raise RuntimeError('Current G2 certification required')
    sample=json.loads((PROJECT/'data/processed/pilot_observers.json').read_text(encoding='utf-8'))
    selected=[o for tercile in (1,2,3) for o in [s for s in sample if s['elevation_tercile']==tercile][:2]]
    spec=model_specification()
    result=schedule(selected,spec=spec,phase='benchmark',run=run,workers=3,maximum_seconds=900)
    reference=json.loads((PROJECT/'data/processed/g3_benchmark_measured.json').read_text(encoding='utf-8'))
    original={c['observer']['observer_id']:c for c in reference['cases']}
    checks=[];baseline=0
    for oid,path in result['completed_checkpoints'].items():
        case=json.loads((PROJECT/path).read_text(encoding='utf-8'));prior=original[oid]
        baseline+=prior['timings']['case_wall_seconds']
        checks.append({'observer_id':oid,'terrain_area_equal':abs(case['terrain']['visible_area_km2']-prior['terrain']['visible_area_km2'])<1e-8,
            'visible_peak_count_equal':case['peaks']['visible_peak_ground_proxies']==prior['peaks']['visible_peak_ground_proxies'],
            'lake_records_sampled':case['landmarks']['lake_records_sampled']})
    passed=(result['state']=='complete' and result['resource_events']==0 and len(checks)==6
        and result['maximum_active_workers']==3 and result['wall_seconds']<baseline
        and all(c['terrain_area_equal'] and c['visible_peak_count_equal'] and c['lake_records_sampled']==0 for c in checks))
    result['passed']=passed;result['comparison_checks']=checks
    result['sequential_reference_seconds']=baseline
    result['measured_speedup']=baseline/result['wall_seconds']
    result['scaled_full_cohort_hours']=result['wall_seconds']/6*1302/3600
    atomic_json(PROJECT/'data/processed/g4_parallel_benchmark.json',result)
    return result


def run_production(run):
    if config()['approvals']['production_analysis'] is not True:raise RuntimeError('Production approval not recorded')
    spec=model_specification()
    benchmark=json.loads((PROJECT/'data/processed/g4_parallel_benchmark.json').read_text(encoding='utf-8'))
    if not benchmark.get('passed') or benchmark['signature']!=specification_key(spec):raise RuntimeError('Matching successful three-worker benchmark required')
    return schedule(observer_records(),spec=spec,phase='production',run=run)
