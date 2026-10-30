"""Independent numerical formulas and manufactured output audits."""
import json
from pathlib import Path
import numpy as np
import pytest
from src.numerical_diagnostics import (observed_orders,scaled_state_error,common_samples,
    metric_changes,rk4_amplification,modal_diagnostics)
from src.experiments import generate_cases
from src.config import case_summary,load_config
from studies.refinement_audit import audit


def test_orders_and_exact_zero_handling():
    assert observed_orders([.2,.1,.05],[.2**4,.1**4,.05**4])==pytest.approx([4,4])
    assert observed_orders([.2,.1],[0,0])==[None]
    with pytest.raises(ValueError): observed_orders([.1,.2],[1,2])


def test_scaled_norm_units_and_quaternion_sign():
    a=np.zeros((3,7));a[:,0]=1;b=a.copy();b[:,0]=-2;b[:,4]=2
    result=scaled_state_error([0,1,4],a,b,2)
    assert result['scaled_time_rms']==1
    assert result['quaternion_chord_max']==0
    assert result['reference_quaternion_norm_defect_max']==1
    with pytest.raises(ValueError):scaled_state_error([0,1,4],a,b,0)


def test_nested_nodes_reject_reference_interpolation():
    y=np.zeros((5,7));y[:,0]=1
    assert common_samples([0,1,2],np.linspace(0,2,5),y).shape==(3,7)
    with pytest.raises(ValueError):common_samples([0,.8,2],np.linspace(0,2,5),y)


def test_modal_walls_and_neutral_modes():
    assert rk4_amplification(-2)==pytest.approx(1/3)
    assert abs(rk4_amplification(-2.78))<1
    assert abs(rk4_amplification(-2.79))>1
    a=modal_diagnostics(np.diag([-2.,-2000.,0]),.001)
    b=modal_diagnostics(np.diag([-2.,-2000.,0]),.002)
    assert a['neutral_mode_count']==1 and a['non_growing_modes_outside_rk4']==0
    assert b['non_growing_modes_outside_rk4']==1
    assert a['decaying_mode_magnitude_ratio']==1000


def test_growing_modes_are_reported_separately():
    x=modal_diagnostics(np.diag([1.,0]),.1)
    assert x['growing_mode_count']==1 and x['non_growing_modes_outside_rk4']==0
    assert x['decaying_mode_magnitude_ratio'] is None


def test_censor_switch_has_no_fake_time_difference():
    a=dict(success=False,detumbling_time_s=None,final_rate_rad_s=1,
           saturation_fraction=0,peak_torque_Nm=0,dipole_effort_Am2_s=0)
    b=dict(a,success=True,detumbling_time_s=3)
    c=metric_changes(a,b)
    assert c['success_changed'] and c['detumbling_time_change_s'] is None


def test_cases_derive_deadline_from_canonical_baseline():
    c=json.loads(Path('configs/study.json').read_text())
    case=next(generate_cases(c));timing=case_summary(load_config())
    assert case['metrics']['deadline_s']==timing['deadline_s']
    assert case['document']['physical']==case['config']
    assert case['document']['initial_conditions']['quaternion']==case['y0'][:4]


def test_manufactured_output_audit():
    # A prescribed h**4 perturbation tests diagnostics, not any time integrator.
    case=dict(metrics=dict(deadline_s=4,hold_s=1,threshold_rad_s=1),dipole_limit_Am2=1)
    def output(case,h):
        t=np.linspace(0,4,round(4/h)+1);y=np.zeros((len(t),7));y[:,0]=1;y[:,4]=np.exp(-t)+h**4
        z=np.zeros((len(t),3))
        return dict(t=t,states=y,raw_dipole=z,dipole=z,torque=z)
    result,_=audit(case,output,.25)
    assert result['observed_difference_order']==pytest.approx(4)
    assert result['approved'] is False
    assert len(result['output_only_metric_changes'])==2
