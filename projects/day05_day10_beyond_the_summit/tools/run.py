"""Run the CLI/test runner inside the isolated environment, without activation."""
from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import uuid

project=Path(__file__).resolve().parents[1]
environment=os.environ.copy()
environment['PYTHONPATH']=str(project/'src')
environment['PYTHONNOUSERSITE']='1'
environment['PYTHONUTF8']='1'
environment['PYTHONIOENCODING']='utf-8'
environment['MPLBACKEND']='Agg'
environment['MPLCONFIGDIR']=str(project/'.runtime/matplotlib')
environment['OPENBLAS_NUM_THREADS']='1'
environment['OMP_NUM_THREADS']='1'
environment['GDAL_CACHEMAX']='128'
runtime=project.parents[1]/'.bts'
temporary=runtime/'tmp'
temporary.mkdir(parents=True,exist_ok=True)
environment['TEMP']=environment['TMP']=str(temporary)
environment['MAMBA_ROOT_PREFIX']=str(runtime/'mamba')
prefix=runtime/'env'
environment['CONDA_PREFIX']=str(prefix)
environment['PATH']=os.pathsep.join(str(p) for p in [prefix,prefix/'Library/bin',prefix/'Scripts'])+os.pathsep+environment.get('PATH','')
environment['PROJ_DATA']=str(prefix/'Library/share/proj')
environment['GDAL_DATA']=str(prefix/'Library/share/gdal')
# Direct interpreter invocation avoids micromamba run's global AppData proc
# directory, which this workspace sandbox does not allow. Keep the DLL-directory
# handle alive for the duration of runpy, including pytest imports.
bootstrap="import os,runpy,sys; _dll=os.add_dll_directory(os.path.join(sys.prefix,'Library','bin')) if os.name=='nt' else None; module=sys.argv.pop(1); sys.argv[0]=module; runpy.run_module(module,run_name='__main__',alter_sys=True)"
command=[str(prefix/'python.exe'),'-c',bootstrap]
if len(sys.argv)>1 and sys.argv[1]=='test':
    command.extend(['pytest','-p','no:cacheprovider','--basetemp',str(temporary/('pytest-'+uuid.uuid4().hex)),*sys.argv[2:]])
else:
    command.extend(['beyond_the_summit',*sys.argv[1:]])
raise SystemExit(subprocess.call(command,cwd=project,env=environment))
