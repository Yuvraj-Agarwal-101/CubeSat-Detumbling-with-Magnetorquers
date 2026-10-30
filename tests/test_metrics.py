import numpy as np
import pytest
from src.metrics import detumbling_time, saturation_fraction, compute_metrics
from studies.fixtures import simulate


def test_crossing_and_complete_hold():
    assert detumbling_time([0,10,20],[2,0,0],1,15,20)==5
    assert detumbling_time([0,10,20],[2,0,0],1,16,20) is None


def test_excursion_resets_hold():
    assert detumbling_time([0,2,3,4,10],[0,0,2,0,0],1,5,10)==3.5


def test_equality_and_deadline_clipping():
    assert detumbling_time([0,20],[1,1],1,10,10)==0
    assert detumbling_time([0,20],[0,2],1,11,12) is None


@pytest.mark.parametrize('t,r', [([0,1],[0,float('nan')]),([0,0],[0,0]),([1,2],[0,0]),([0,1],[0,-1])])
def test_invalid_histories(t,r):
    with pytest.raises(ValueError): detumbling_time(t,r,1,1,2)


def test_time_weighted_saturation():
    assert saturation_fraction([0,1,10],[2,2,0],1)==pytest.approx(.55)
    assert saturation_fraction([0,10],[1,1],1)==0
    assert saturation_fraction([0,10],[0,2],1)==.5


def test_metrics_known_vectors():
    y=np.zeros((3,7));y[:,0]=1
    raw=np.tile([2.,0,0],(3,1));m=raw/2;torque=m*3
    result=compute_metrics([0,3,10],y,raw,m,torque,
        dict(deadline_s=10,threshold_rad_s=1,hold_s=10),1)
    assert result['success'] and result['detumbling_time_s']==0
    assert result['dipole_effort_Am2_s']==10
    assert result['peak_torque_Nm']==3
    assert result['saturation_fraction']==1


def test_refined_grid_threshold():
    # Known exponential crossing; this checks metric output-grid convergence only.
    exact=np.log(4)
    errors=[]
    for h in [.2,.1,.05,.0125]:
        t=np.arange(0,4+h/2,h)
        errors.append(abs(detumbling_time(t,4*np.exp(-t),1,1,4)-exact))
        assert errors[-1] < h*h/4
    assert errors[-1]<errors[0]/16
