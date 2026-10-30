import numpy as np
import pytest
from src.integrators import rk4
from src.numerical_analysis import trajectory_error_norms, rk4_amplification, frozen_linear_diagnostics


def test_time_weighted_norm_is_independent_of_grid_length():
    for t in ([0,.5,1.], [0,.3,.6,.9,1.]):
        norms=trajectory_error_norms(t, np.tile([3.,4.],(len(t),1)))
        assert norms['l2_time'] == pytest.approx(5)
        assert norms['linfinity_sampled'] == pytest.approx(5)


def test_complex_eigenvalue_matches_real_two_component_rotation():
    h=.2
    matrix=np.array([[0.,-1.],[1.,0.]])
    result=rk4(lambda t,y:matrix@y,[1.,0.],(0,h),h)
    observed=result.states[-1,0]+1j*result.states[-1,1]
    assert observed == pytest.approx(rk4_amplification(1j*h))


def test_local_defect_and_lecture_normalized_truncation_orders():
    errors=[]
    for h in [.2,.1,.05]:
        result=rk4(lambda t,y:y,[1.],(0,h),h)
        errors.append(abs(np.expm1(h)-(result.states[-1,0]-1)))
    orders=np.log2(np.array(errors[:-1])/errors[1:])
    assert np.all((orders>4.9)&(orders<5.2))
    assert np.all((orders-1>3.9)&(orders-1<4.2))


def test_lecture_fast_mode_crosses_the_rk4_stability_boundary():
    matrix=np.array([[-2.,0.],[400.,-2000.]])
    a=frozen_linear_diagnostics(matrix,.001)
    b=frozen_linear_diagnostics(matrix,.0015)
    assert a['nonzero_mode_ratio'] == pytest.approx(1000)
    assert a['decaying_modes_outside_region'] == 0
    assert b['decaying_modes_outside_region'] == 1


def test_zero_modes_are_reported_separately():
    result=frozen_linear_diagnostics(np.diag([0.,-2.,-2000.]),.001)
    assert result['neutral_modes'] == 1
    assert result['nonzero_mode_ratio'] == pytest.approx(1000)


def test_real_state_integrator_rejects_complex_data():
    with pytest.raises(ValueError):
        rk4(lambda t,y:y, [1+1j], (0,1),.1)
    with pytest.raises(ValueError):
        rk4(lambda t,y:np.array([1j]), [1.], (0,1),.1)
