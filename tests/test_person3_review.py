"""Independent Person 3 checks of the merged production callbacks and wiring."""
from copy import deepcopy

import numpy as np
import pytest

import team_adapter
from src.config import load_config, runtime_config, initial_state
from src.controller import controller
from src.dynamics import rhs
from src.orbit_field import circular_orbit, dipole_axis, field_model


def runtime():
    return runtime_config(load_config(), field_model=field_model, controller=controller)


def passive(q):
    # Independent scalar-first matrix, expanded componentwise.
    s, x, y, z = q / np.linalg.norm(q)
    return np.array([[1-2*(y*y+z*z), 2*(x*y+s*z), 2*(x*z-s*y)],
                     [2*(x*y-s*z), 1-2*(x*x+z*z), 2*(y*z+s*x)],
                     [2*(x*z+s*y), 2*(y*z-s*x), 1-2*(x*x+y*y)]])


def test_orbit_period_is_not_magnetic_period_and_velocity_is_derivative():
    c = runtime()
    c['orbit'].update(raan_rad=.7, phase_rad=.4)
    radius = c['orbit']['earth_radius_m'] + c['orbit']['altitude_m']
    n = np.sqrt(c['orbit']['gravitational_parameter_m3_s2']/radius**3)
    period = 2*np.pi/n
    for t in [0., 123., 3456.]:
        r, v = circular_orbit(t, c)
        assert np.linalg.norm(r) == pytest.approx(radius, rel=1e-14)
        np.testing.assert_allclose(circular_orbit(t+period, c), (r, v), rtol=1e-12, atol=1e-7)
        fd = (circular_orbit(t+.1, c)[0]-circular_orbit(t-.1, c)[0])/.2
        np.testing.assert_allclose(fd, v, rtol=1e-8, atol=1e-6)
    assert np.linalg.norm(field_model(period, c)[0]-field_model(0., c)[0]) > 1e-7
    c['magnetic']['earth_rotation_rate_rad_s'] = 0.
    np.testing.assert_allclose(field_model(period, c)[0], field_model(0., c)[0], atol=1e-18)


def test_inverse_cube_scaling_and_rotating_axis():
    c = runtime()
    c['orbit'].update(raan_rad=.6, phase_rad=.8)
    original = field_model(0., c)[0]
    radius = c['orbit']['earth_radius_m'] + c['orbit']['altitude_m']
    c['orbit']['altitude_m'] = 2*radius-c['orbit']['earth_radius_m']
    np.testing.assert_allclose(field_model(0., c)[0], original/8, rtol=1e-14, atol=1e-20)
    rate = c['magnetic']['earth_rotation_rate_rad_s']
    c['magnetic']['earth_rotation_phase_rad'] = .3
    d0, _ = dipole_axis(0., c)
    d, dd = dipole_axis(np.pi/(2*rate), c)
    np.testing.assert_allclose(d, [-d0[1], d0[0], d0[2]], atol=1e-15)
    assert d@d == pytest.approx(1., abs=1e-15)
    np.testing.assert_allclose(dd, rate*np.cross([0, 0, 1], d), atol=1e-20)


@pytest.mark.parametrize('rate', [0., 7.292115e-5, .002])
def test_derivative_refinement_with_nonzero_phases(rate):
    c = runtime()
    c['orbit'].update(raan_rad=.9, phase_rad=.6, inclination_rad=1.2)
    c['magnetic'].update(earth_rotation_phase_rad=.7, earth_rotation_rate_rad_s=rate)
    t = 789.
    exact = field_model(t, c)[1]
    errors = [np.linalg.norm((field_model(t+h, c)[0]-field_model(t-h, c)[0])/(2*h)-exact)
              for h in [4., 2., 1., .5]]
    np.testing.assert_allclose(np.array(errors[:-1])/errors[1:], 4., rtol=.001)


@pytest.mark.parametrize('factor', [.5, 1., 2.])
def test_oblique_vector_saturation_boundary_and_input_purity(factor):
    c = runtime()
    c['controller_settings'].update(gain_kg_m2_s=1., max_dipole_a_m2=1.)
    b = np.array([1., 0., 0.])
    db = -factor*np.array([0., .6, .8])
    before = deepcopy(c)
    b0, db0 = b.copy(), db.copy()
    result = controller(7., None, None, b, db, c)
    np.testing.assert_allclose(result['raw_dipole'], -db, atol=1e-15)
    np.testing.assert_allclose(result['dipole'], [0., min(factor, 1)*.6, min(factor, 1)*.8])
    assert result['saturated'] == (factor > 1.)
    assert np.linalg.norm(result['dipole']) <= 1.
    assert result['torque']@b == pytest.approx(0., abs=1e-15)
    controller(99., None, None, [1., 2., 3.], [3., 1., 2.], c)
    repeated = controller(7., None, None, b, db, c)
    for key in result:
        np.testing.assert_array_equal(result[key], repeated[key])
    np.testing.assert_array_equal(b, b0)
    np.testing.assert_array_equal(db, db0)
    np.testing.assert_array_equal(c.pop('inertia'), before.pop('inertia'))
    assert c == before


@pytest.mark.parametrize('q', [[1., 0., 0., 0.], [2**-.5, 0., 0., 2**-.5], [.7, -.2, .4, .3]])
@pytest.mark.parametrize('t,w', [(0., [0., 0., 0.]), (123., [.1, -.2, .3]), (3456., [-.02, .04, .01])])
def test_complete_rhs_independent_assembly(q, t, w):
    c = runtime()
    y = np.r_[q, w]
    saved = y.copy()
    matrix = passive(np.array(q))
    bi, dbi = field_model(t, c)
    b = matrix@bi
    db = matrix@dbi-np.cross(w, b)
    k = c['controller_settings']['gain_kg_m2_s']
    m = -k*db/(b@b)
    m *= min(1., c['controller_settings']['max_dipole_a_m2']/np.linalg.norm(m))
    torque = np.cross(m, b)
    qdot = .5*np.r_[-np.dot(q[1:], w), q[0]*np.array(w)+np.cross(q[1:], w)]
    acceleration = np.linalg.solve(c['inertia'], torque-np.cross(w, c['inertia']@w))
    np.testing.assert_allclose(rhs(t, y, c), np.r_[qdot, acceleration], rtol=1e-12, atol=1e-17)
    np.testing.assert_array_equal(y, saved)
    # Differentiate the rotating body field using independent matrix kinematics.
    h = 1e-3
    fd = (passive(np.array(q)+h*qdot)@field_model(t+h, c)[0]
          -passive(np.array(q)-h*qdot)@field_model(t-h, c)[0])/(2*h)
    np.testing.assert_allclose(fd, db, rtol=1e-7, atol=1e-14)


def test_real_adapter_uses_each_rk4_stage_time_and_state(monkeypatch):
    calls = []
    def observed(t, q, w, b, db, c):
        calls.append((t, np.r_[q, w]))
        return controller(t, q, w, b, db, c)
    monkeypatch.setattr(team_adapter, 'controller', observed)
    doc = deepcopy(load_config())
    doc['study'].update(deadline_orbits=.00001, hold_duration_s=.001)
    output = team_adapter.simulate(dict(document=doc), 1.)
    h = output['t'][-1]
    c = runtime_config(doc, field_model=field_model, controller=controller)
    y = initial_state(doc)
    k1 = rhs(0., y, c)
    k2 = rhs(h/2, y+h*k1/2, c)
    k3 = rhs(h/2, y+h*k2/2, c)
    expected = [(0., y), (h/2, y+h*k1/2), (h/2, y+h*k2/2), (h, y+h*k3)]
    assert len(calls) == 6  # Four stages plus diagnostics at two output nodes.
    for (t, state), (te, ye) in zip(calls[:4], expected):
        assert t == te
        np.testing.assert_allclose(state, ye, rtol=0, atol=1e-16)


@pytest.mark.parametrize('w', [[.1, -.2, .3], [.1, .2, -.3], [0., 0., 0.]])
def test_static_inertial_field_rotational_power(w):
    c = runtime()
    c['controller_settings']['max_dipole_a_m2'] = 100.
    b = np.array([1e-5, 2e-5, -3e-5])
    w = np.array(w)
    command = controller(0., None, w, b, -np.cross(w, b), c)
    perpendicular = w-b*(w@b)/(b@b)
    power = -c['controller_settings']['gain_kg_m2_s']*(perpendicular@perpendicular)
    assert not command['saturated']
    assert w@command['torque'] == pytest.approx(power, rel=1e-13, abs=1e-22)
