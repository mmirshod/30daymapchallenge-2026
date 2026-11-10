from __future__ import annotations

import json
from pathlib import Path

import typer

from .runtime import Run, config, require_resources

app=typer.Typer(no_args_is_help=True,pretty_exceptions_enable=False)


def display(value: object) -> None:
    typer.echo(json.dumps(value,indent=2,ensure_ascii=False,default=str))


@app.command()
def doctor():
    """Report interpreter, native GIS and measured resource readiness."""
    from .doctor import inspect_environment
    with Run('doctor').capture():
        display(inspect_environment())


@app.command()
def prepare():
    """Stage/validate approved existing sources; never overwrite prior days."""
    from .prepare import prepare_existing
    with Run('prepare').capture() as run:
        display(prepare_existing(run))


@app.command()
def acquire(execute: bool=typer.Option(False,'--execute'),radius_m: int=100000):
    """Plan missing DEM tiles; --execute downloads after resource checks."""
    from .acquire import acquire_dem
    with Run('acquire',{'execute':execute,'radius_m':radius_m}).capture() as run:
        display(acquire_dem(run,execute=execute,radius_m=radius_m))


@app.command('native-smoke')
def native_smoke():
    """Validate the native backend on tiny synthetic terrains."""
    from .validation import native_smoke_tests
    with Run('native-smoke').capture() as run:
        require_resources(config(),pilot=True)
        display(native_smoke_tests(run))


@app.command('prepare-pilot-dem')
def prepare_pilot_dem(resolution: int=90):
    """Build a same-source pilot DEM after all 100 km tiles are present."""
    from .pilot_terrain import build_pilot_terrain
    result=build_pilot_terrain(resolution)
    display({k:v for k,v in result.items() if k!='specification'})


@app.command('gdal-smoke')
def gdal_smoke(entry_available_ram_gib: float = 4):
    """Validate the selected GDAL adapter on bounded synthetic terrain."""
    from .gdal_smoke import smoke_tests
    with Run('gdal-smoke').capture() as run:
        display(smoke_tests(run,entry_available_ram_gib=entry_available_ram_gib))


@app.command('data-readiness')
def data_readiness(stage: str='all',entry_available_ram_gib: float=2):
    """G2: certify terrain and prepare cross-border targets/landmark evidence."""
    from .data_readiness import run_readiness
    with Run('data-readiness',{'stage':stage,'entry_available_ram_gib':entry_available_ram_gib}).capture() as run:
        display(run_readiness(run,stage,entry_available_ram_gib))


@app.command('g3-benchmark')
def g3_benchmark(entry_available_ram_gib: float=2):
    """Run the twelve-observer sequential end-to-end benchmark, never production."""
    from .g3_benchmark import run_g3
    with Run('g3-benchmark',{'entry_available_ram_gib':entry_available_ram_gib}).capture() as run:
        display(run_g3(run,entry_available_ram_gib=entry_available_ram_gib))


@app.command('g3-report')
def g3_report():
    """Build measured G3 figures and a checkpoint report."""
    from .g3_report import report_g3
    with Run('g3-report').capture():display(report_g3())


@app.command('parallel-benchmark')
def parallel_benchmark():
    """Test three concurrent full observers against G3 results."""
    from .analysis import parallel_benchmark as benchmark
    with Run('parallel-benchmark').capture() as run:
        result=benchmark(run)
        display({k:v for k,v in result.items() if k not in ('completed_checkpoints','model_specification')})


@app.command('analysis-control')
def analysis_control(workers: int):
    """Set live workers to 0 (drain/pause), 1, 2 or 3 without invalidating work."""
    from .analysis import set_control
    display(set_control(workers))


@app.command('analysis-status')
def analysis_status():
    """Read progress without starting analysis."""
    from .analysis import STATUS
    data=json.loads(STATUS.read_text(encoding='utf-8'))
    display({k:v for k,v in data.items() if k not in ('completed_checkpoints','model_specification')})


@app.command('rank')
def rank():
    """G5: verify completed G4, calculate NPS and weight sensitivity."""
    from .ranking import run_rank
    with Run('g5-ranking').capture() as run:
        result=run_rank(run)
        display({k:v for k,v in result.items() if k not in ('outputs','inputs')})


@app.command('ranking-report')
def ranking_report():
    """Validate and render G5 tables, statistics and robustness figures."""
    from .ranking_report import report_rankings
    with Run('g5-report').capture():display(report_rankings())


@app.command('rank-mps')
def rank_mps():
    """Calculate Horizon-only MPS from existing, hash-checked G4/G5 products."""
    from .mps import main
    with Run('g5-mps').capture():main()


@app.command('export-publication')
def export_publication():
    """G6: generate local PDF/PNG reports and static explorer; no publication."""
    from .publication import build_publication
    with Run('g6-export').capture():display(build_publication())


@app.command('stage-pages')
def stage_pages_command():
    """Stage verified G6 assets under docs/day05 without a commit or deployment."""
    from .publication import stage_pages
    with Run('g6-stage-pages').capture():display(stage_pages())


@app.command()
def pilot(phase: str='local'):
    """Run the bounded pilot only when resources and prerequisites pass."""
    cfg=config()
    with Run('pilot',{'phase':phase}).capture():
        require_resources(cfg,pilot=True)
        from .pilot import run_pilot
        report=run_pilot(cfg,phase=phase)
        display({k:v for k,v in report.items() if k!='cases'})


@app.command()
def analyze():
    """Production analysis is gated on pilot review."""
    if not config()['approvals']['production_analysis']:
        raise typer.BadParameter('Production analysis requires recorded pilot review and budget approval')
    from .analysis import run_production
    with Run('g4-analysis').capture() as run:
        result=run_production(run)
        display({k:v for k,v in result.items() if k not in ('completed_checkpoints','model_specification')})


@app.command('pilot-report')
def pilot_report():
    """Summarize measured pilot artifacts without approving production."""
    from .pilot_report import summarize_pilot
    with Run('pilot-report').capture():display(summarize_pilot())


@app.command('pilot-gdal')
def pilot_gdal():
    """Cross-check three 30 m cases with independent GDAL viewsheds."""
    from .pilot_gdal import benchmark_gdal
    with Run('pilot-gdal').capture():
        report=benchmark_gdal()
        display({'cases':len(report['cases']),'production_backend_changed':False})


@app.command()
def validate():
    """Check available local preparation and native validation evidence."""
    from .validation import validate_artifacts
    with Run('validate').capture():
        display(validate_artifacts())


@app.command('all')
def run_all():
    """Advance through implemented stages; stop at unmet readiness gates."""
    doctor()
    prepare()
    native_smoke()
    pilot()


if __name__=='__main__':
    app()

