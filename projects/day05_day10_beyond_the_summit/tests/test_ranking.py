import numpy as np
import pandas as pd
import pytest
import yaml

from beyond_the_summit.ranking import percentile_score,component_scores,weighted_score,stable_order,skyline_metrics
from beyond_the_summit.runtime import PROJECT


def rules():return yaml.safe_load((PROJECT/'config/ranking.yaml').read_text(encoding='utf-8'))


def test_percentile_ties_zeros_constants_and_missing():
    assert np.allclose(percentile_score([0,2,2,8]),[0,50,50,87.5])
    assert np.all(percentile_score([0,0,0])==0)
    assert np.all(percentile_score([5,5,5])==50)
    assert np.isnan(percentile_score([np.nan])[0])
    with pytest.raises(ValueError):percentile_score([-1,2])


def test_missing_component_is_not_imputed_and_ties_are_deterministic():
    frame=pd.DataFrame({'terrain':[100,np.nan],'peaks':[100,100],'skyline':[100,100],'distance':[100,100]})
    weights={'terrain':.3,'peaks':.25,'skyline':.3,'distance':.15}
    result=weighted_score(frame,weights)
    assert np.isclose(result[0],100) and np.isnan(result[1])
    assert stable_order(['z','a','b'],[5,5,7]).tolist()==[2,1,0]
    with pytest.raises(ValueError):weighted_score(frame,{k:.4 for k in weights})


def test_zero_evidence_does_not_get_a_mean_score():
    names=['visible_area_km2','visible_peak_ground_proxies','skyline_prominence_sum_degrees','skyline_complexity',
           'terrain_distance_proxy_km','peak_angular_relief_degrees','open_directions_fraction','peak_bearing_coverage_fraction']
    frame=pd.DataFrame({n:[0.,0.] for n in names})
    result=component_scores(frame,rules())
    assert (result[['terrain','peaks','skyline','distance']].to_numpy()==0).all()


def test_signed_circular_multiscale_skyline_and_nearfield_ablation():
    x=np.arange(3600)*np.pi/1800
    values=-5+2*np.cos(4*x)
    def profile(a,distance=10000):
        return {'horizon_degrees':a.tolist(),'limiting_distance_projected_m':[distance]*3600,'angular_step_degrees':.1}
    base=skyline_metrics(profile(values),rules())
    shifted=skyline_metrics(profile(np.roll(values+10,137)),rules())
    assert base['skyline_prominence_sum_degrees']>0
    assert np.isclose(base['skyline_prominence_sum_degrees'],shifted['skyline_prominence_sum_degrees'])
    assert np.isclose(base['skyline_complexity'],shifted['skyline_complexity'])
    near=skyline_metrics(profile(values,100),rules())
    assert near['nearfield_horizon_fraction']==1 and near['skyline_far_strength']==0
    assert near['skyline_far_complexity']==0
