"""Real dynamics and RK4 with artificial zero torque control, not a flight model."""
import numpy as np
from src.dynamics import rhs
from src.integrators import rk4
from src.quaternion import rotation_matrix
from tests.exact_cases import exact_rotation, attitude_error, project_quaternion


def artificial_field(t, config):
    return np.array([2e-5, -1e-5, 3e-5]), np.zeros(3)


def zero_dipole(t, q, omega, b, db, config):
    return dict(raw_dipole=np.zeros(3), dipole=np.zeros(3),
                torque=np.zeros(3), saturated=False)


def test_shared_rhs_spherical_exact_convergence():
    config = dict(inertia=.02*np.eye(3), field_model=artificial_field, controller=zero_dipole)
    initial = np.array([.8, .2, -.4, .4, .3, -.4, .5])
    exact = exact_rotation(20, initial[:4], initial[4:])
    errors = []
    for step in (.5, .25, .125):
        result = rk4(lambda t, y: rhs(t, y, config), initial, (0, 20), step,
                     projection=project_quaternion)
        errors.append(attitude_error(result.states[-1, :4], exact))
        np.testing.assert_allclose(result.states[-1, 4:], initial[4:], atol=1e-14, rtol=0)
    np.testing.assert_allclose(np.log2(np.array(errors[:-1])/errors[1:]), 4, atol=.03)


def test_shared_rhs_callbacks_receive_all_four_stage_states():
    times, states = [], []
    def field(t, config):
        times.append(t)
        return artificial_field(t, config)
    def control(t, q, omega, b, db, config):
        states.append(np.r_[q, omega])
        return zero_dipole(t, q, omega, b, db, config)
    config = dict(inertia=.02*np.eye(3), field_model=field, controller=control)
    initial = np.array([1., 0, 0, 0, .3, -.4, .5])
    result = rk4(lambda t, y: rhs(t, y, config), initial, (0, .2), .2,
                 projection=project_quaternion)
    np.testing.assert_allclose(times, [0, .1, .1, .2])
    assert len(states) == result.function_evaluations == 4
    assert not np.array_equal(states[1], states[2])
    assert np.linalg.norm(states[1][:4]) > 1
    np.testing.assert_allclose(np.linalg.norm(result.states[-1, :4]), 1, atol=1e-15)


def test_asymmetric_torque_free_invariants_improve_under_refinement():
    inertia = np.diag([.030, .035, .007])
    config = dict(inertia=inertia, field_model=artificial_field, controller=zero_dipole)
    initial = np.array([.8, .2, -.4, .4, .3, -.4, .5])
    errors = []
    for step in (.2, .1):
        result = rk4(lambda t, y: rhs(t, y, config), initial, (0, 10), step,
                     projection=project_quaternion)
        rates = result.states[:, 4:]
        energy = .5*np.einsum('ni,ij,nj->n', rates, inertia, rates)
        momentum = np.array([rotation_matrix(y[:4]).T @ inertia @ y[4:]
                             for y in result.states])
        errors.append([np.max(abs(energy-energy[0]))/energy[0],
                       np.max(np.linalg.norm(momentum-momentum[0], axis=1))/np.linalg.norm(momentum[0])])
    assert np.all(np.array(errors[1]) < np.array(errors[0])/8)
    assert max(errors[1]) < 1e-6
