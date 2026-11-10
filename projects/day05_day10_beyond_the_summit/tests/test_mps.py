import pytest
from beyond_the_summit.mps import landmark_score

def test_fixed_denominator_and_zero():
    assert landmark_score(0,0,0)==0
    assert landmark_score(15,15,15)==pytest.approx(100)
    assert landmark_score(1,0,0)==pytest.approx(70/15)
    with pytest.raises(ValueError):landmark_score(1,1,1,0)

def test_unknown_bound_is_monotone():
    lower=landmark_score(2,.7,.4)
    upper=landmark_score(3,1.2,.6)
    assert 0<lower<upper<100

def test_completed_mps_artifacts_preserve_nps_and_formula():
    """Validate real outputs against their independent frozen NPS source."""
    import json
    import numpy as np
    import pandas as pd
    from beyond_the_summit.runtime import PROJECT, fingerprint
    root=PROJECT/'data/processed'
    if not (root/'mps/summary.json').exists():pytest.skip('MPS not calculated yet')
    summary=json.loads((root/'mps/summary.json').read_text())
    for name,sha in summary['outputs'].items():assert fingerprint(root/'mps'/name)==sha
    original=pd.read_parquet(root/'g5/rankings.parquet').set_index('observer_id')
    scores=pd.read_parquet(root/'mps/rankings.parquet').set_index('observer_id')
    assert len(scores)==1302 and scores.index.is_unique
    assert set(scores.index)==set(original.index)
    assert np.array_equal(scores.nps,original.loc[scores.index,'nps'])
    assert np.allclose(scores.mps,.8*scores.nps+.2*scores.landmark_score_lower)
    assert scores.visible_horizon_count.between(0,15).all()
    assert scores.landmark_score_lower.between(0,100).all()
    assert (scores.mps_upper>=scores.mps).all()
    registry=pd.read_csv(root/'mps/horizon_registry.csv')
    assert len(registry)==15 and registry.target_id.is_unique
    assert registry.coordinate_difference_m.max()<1
    manifest=json.loads((root/'g5_manifest.json').read_text())
    key=next(k for k in manifest['files'] if k.replace('\\','/').endswith('g5/rankings.parquet'))
    assert fingerprint(root/'g5/rankings.parquet')==manifest['files'][key]
