"""Independent geometry, derivative and power identities for the real model."""
from copy import deepcopy
import numpy as np
import pytest
from src.config import load_config, runtime_config, case_summary, initial_state
from src.orbit_field import circular_orbit, dipole_axis, field_model, frozen_inertial_field
from src.controller import controller
from src.dynamics import rhs
from team_adapter import diagnostics, simulate, rhs_for_case


def config():
    return runtime_config(load_config(),field_model=field_model,controller=controller)


def test_circular_orbit_geometry_and_period():
    c=config(); period=case_summary(load_config())['orbital_period_s']
    r,v=circular_orbit(0,c); radius=c['orbit']['earth_radius_m']+c['orbit']['altitude_m']
    np.testing.assert_allclose(r,[radius,0,0],atol=1e-8)
    assert r@v == pytest.approx(0,abs=1e-7)
    assert np.linalg.norm(v)**2 == pytest.approx(c['orbit']['gravitational_parameter_m3_s2']/radius)
    np.testing.assert_allclose(circular_orbit(period,c)[0],r,atol=1e-7)
    d,dd=dipole_axis(123,c)
    assert d@d == pytest.approx(1)
    assert d@dd == pytest.approx(0,abs=1e-18)


def test_active_orbit_rotation_convention():
    c=config(); c['orbit'].update(raan_rad=np.pi/2,inclination_rad=np.pi/2,phase_rad=np.pi/2)
    r,v=circular_orbit(0,c)
    np.testing.assert_allclose(r/np.linalg.norm(r),[0,0,1],atol=1e-15)
    np.testing.assert_allclose(v/np.linalg.norm(v),[0,-1,0],atol=1e-15)


def test_equatorial_and_polar_dipole_limits():
    c=config(); c['magnetic']['dipole_tilt_rad']=0
    r=c['orbit']['earth_radius_m']+c['orbit']['altitude_m']
    b=c['magnetic']['equatorial_surface_field_t']*(c['orbit']['earth_radius_m']/r)**3
    np.testing.assert_allclose(field_model(0,c)[0],[0,0,-b],atol=1e-18)
    c['orbit'].update(inclination_rad=np.pi/2,phase_rad=np.pi/2)
    np.testing.assert_allclose(field_model(0,c)[0],[0,0,2*b],atol=1e-18)


@pytest.mark.parametrize('t',[0.,123.,3456.])
def test_total_field_derivative_against_centered_differences(t):
    c=config(); analytical=field_model(t,c)[1]
    errors=[]
    for h in [2.,1.,.5]:
        difference=(field_model(t+h,c)[0]-field_model(t-h,c)[0])/(2*h)
        errors.append(np.linalg.norm(difference-analytical))
    assert errors[-1] < errors[0]/10
    np.testing.assert_allclose(difference,analytical,rtol=1e-6,atol=1e-15)


def test_frozen_inertial_field_has_zero_inertial_derivative():
    c=config()
    np.testing.assert_array_equal(frozen_inertial_field(100,c)[0],field_model(0,c)[0])
    np.testing.assert_array_equal(frozen_inertial_field(100,c)[1],np.zeros(3))


@pytest.mark.parametrize('limit',[1.,.001])
def test_static_field_power_identity_and_vector_saturation(limit):
    c=config(); c['controller_settings']['max_dipole_a_m2']=limit
    b=np.array([1e-5,2e-5,-3e-5]); w=np.array([.1,-.2,.3])
    d=controller(0,[1,0,0,0],w,b,-np.cross(w,b),c)
    k=c['controller_settings']['gain_kg_m2_s']
    expected=-k*(w-b*(w@b)/(b@b))
    scale=min(1.,limit/np.linalg.norm(d['raw_dipole']))
    np.testing.assert_allclose(d['torque'],scale*expected,rtol=1e-12,atol=1e-18)
    assert w@d['torque'] <= 0
    assert abs(b@d['torque']) < 1e-23
    assert np.linalg.norm(d['dipole']) <= limit*(1+1e-14)
    np.testing.assert_allclose(d['dipole'],scale*d['raw_dipole'])


def test_zero_and_exact_boundary_commands():
    c=config(); c['controller_settings'].update(gain_kg_m2_s=1.,max_dipole_a_m2=1.)
    zero=controller(0,None,None,[1,0,0],[0,0,0],c)
    np.testing.assert_array_equal(zero['dipole'],[0,0,0]); assert not zero['saturated']
    edge=controller(0,None,None,[1,0,0],[0,-1,0],c)
    np.testing.assert_array_equal(edge['dipole'],[0,1,0]); assert not edge['saturated']


@pytest.mark.parametrize('field,derivative', [([0,0,0],[0,0,0]),([np.nan,0,0],[0,0,0]),([1,0,0],[1,2]),([1j,0,0],[0,0,0])])
def test_invalid_controller_vectors(field,derivative):
    with pytest.raises(ValueError): controller(0,None,None,field,derivative,config())


@pytest.mark.parametrize('key,value',[('gain_kg_m2_s',0),('max_dipole_a_m2',-1),('law','other'),('saturation','component')])
def test_invalid_controller_settings(key,value):
    c=config(); c['controller_settings'][key]=value
    with pytest.raises(ValueError): controller(0,None,None,[1,0,0],[0,0,0],c)


def test_real_rhs_diagnostics_consistency_and_no_mutation():
    c=config(); y=initial_state(load_config()); original=y.copy()
    for t in [0,10,100]:
        out=rhs(t,y,c); d=diagnostics(t,y,c)
        np.testing.assert_array_equal(out,rhs_for_case(t,y,dict(document=load_config())))
        np.testing.assert_allclose(c['inertia']@out[4:]+np.cross(y[4:],c['inertia']@y[4:]),d['torque'],atol=1e-18)
        np.testing.assert_array_equal(out,rhs(t,y,c))
    np.testing.assert_array_equal(y,original)


@pytest.mark.parametrize('mode',['orbital','frozen_inertial'])
def test_real_simulation_adapter_returns_complete_short_test_horizon(mode):
    # Short verification interval only; full numerical studies use six orbits.
    document=deepcopy(load_config())
    document['study'].update(deadline_orbits=.001,hold_duration_s=.1)
    case=dict(document=document,field_mode=mode,y0=initial_state(document).tolist())
    output=simulate(case,.25)
    assert output['t'][-1] == case_summary(document)['deadline_s']
    assert output['t'][0] == 0
    for key in ('raw_dipole','dipole','torque'):
        assert output[key].shape == (len(output['t']),3)
        assert np.all(np.isfinite(output[key]))
    np.testing.assert_allclose(np.linalg.norm(output['states'][:,:4],axis=1),1,atol=1e-14)
    np.testing.assert_array_equal(output['states'],simulate(case,.25)['states'])
    assert output['preprojection_norm_error'].shape == output['t'].shape


def test_simulation_adapter_refuses_unknown_field_mode():
    with pytest.raises(ValueError):
        simulate(dict(document=load_config(),field_mode='unknown'),1.)
