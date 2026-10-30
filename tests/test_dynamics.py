"""Instantaneous dynamics checks using explicitly artificial callbacks.

The field and controller fixtures below exercise wiring, not the production
geomagnetic model or B dot controller, which are separate team deliverables.
No numerical time integrator is used in these tests.
"""

import numpy as np
import pytest
from numpy.testing import assert_allclose

from src.dynamics import angular_acceleration, rhs
from src.quaternion import normalize, rotation_matrix


STATE = np.array([1.0, 0, 0, 0, 0.1, 0.2, 0.3])


def fixture_field(t, config):
    """Artificial linear field solely for interface tests."""
    slope = np.array([1e-7, -2e-7, 3e-7])
    return np.array([2e-5, -1e-5, 3e-5]) + t * slope, slope


def fixture_controller(t, q, omega, b_b, db_b_dt, config):
    """Prescribed test dipole, not a B dot implementation."""
    dipole = np.array(config.get("test_dipole", [0.0, 0.0, 0.0]))
    return {"raw_dipole": dipole.copy(), "dipole": dipole.copy(),
            "torque": np.cross(dipole, b_b), "saturated": False}


def fixture_config():
    return {"inertia": np.diag([2.0, 3.0, 4.0]),
            "field_model": fixture_field, "controller": fixture_controller}


def test_diagonal_euler_components_against_hand_calculation():
    expected = [0.17, 0.56 / 3, 0.145]
    observed = angular_acceleration([0.1, 0.2, 0.3], [0.4, 0.5, 0.6], np.diag([2, 3, 4]))
    assert_allclose(observed, expected, atol=1e-15)


def test_spherical_inertia_has_zero_gyroscopic_acceleration():
    omega = [0.3, -0.5, 0.9]
    assert_allclose(angular_acceleration(omega, [0, 0, 0], 2 * np.eye(3)), 0, atol=1e-15)
    assert_allclose(angular_acceleration(omega, [0.4, -0.2, 0.8], 2 * np.eye(3)),
                    [0.2, -0.1, 0.4], atol=1e-15)


def test_zero_rate_acceleration_from_a_full_tensor():
    inertia = np.array([[2.0, 0.2, 0.1], [0.2, 3.0, 0.3], [0.1, 0.3, 4.0]])
    expected = np.array([0.2, -0.3, 0.4])
    assert_allclose(angular_acceleration([0, 0, 0], inertia @ expected, inertia),
                    expected, atol=1e-15)


def test_principal_axis_torque_free_spin_has_zero_acceleration():
    assert_allclose(angular_acceleration([0, 0, 0.6], [0, 0, 0], np.diag([2, 3, 4])), 0)


def test_rhs_has_expected_state_order_and_hand_calculated_values():
    derivative = rhs(0.0, STATE, fixture_config())
    assert derivative.shape == (7,)
    assert_allclose(derivative, [0, 0.05, 0.1, 0.15, -0.03, 0.02, -0.005], atol=1e-15)


def test_rhs_spherical_zero_torque_matches_exact_instantaneous_rotation():
    state = np.array([np.cos(0.4), 0, 0, np.sin(0.4), 0, 0, 0.8])
    config = fixture_config()
    config["inertia"] = 2 * np.eye(3)
    expected = [-0.4 * np.sin(0.4), 0, 0, 0.4 * np.cos(0.4), 0, 0, 0]
    assert_allclose(rhs(1.0, state, config), expected, atol=1e-15)


def test_rhs_uses_dipole_cross_field_with_correct_sign():
    config = fixture_config()
    config["inertia"] = np.eye(3)
    config["field_model"] = lambda t, c: ([0, 0, 2e-5], [0, 0, 0])
    config["test_dipole"] = [0.1, 0, 0]
    state = np.r_[[1.0, 0, 0, 0], [0, 0, 0]]
    assert_allclose(rhs(0, state, config)[4:], [0, -2e-6, 0], atol=1e-18)


def test_orbital_and_body_field_derivatives_reach_controller():
    seen = {}

    def capture(t, q, omega, b_b, db_b_dt, config):
        seen.update(t=t, q=q, omega=omega, field=b_b, derivative=db_b_dt)
        return fixture_controller(t, q, omega, b_b, db_b_dt, config)

    config = fixture_config()
    config["controller"] = capture
    config["field_model"] = lambda t, c: ([1e-5, 2e-5, 3e-5], [4e-7, 5e-7, 6e-7])
    state = np.r_[[np.sqrt(0.5), 0, 0, np.sqrt(0.5)], [0, 0, 0.4]]
    rhs(2.5, state, config)
    # Passive positive quarter turn sends (x, y, z) to (y, -x, z).
    assert_allclose(seen["field"], [2e-5, -1e-5, 3e-5], atol=1e-19)
    # Rotation derivative minus omega cross B gives (-3.5e-6,-8.4e-6,6e-7).
    assert_allclose(seen["derivative"], [-3.5e-6, -8.4e-6, 6e-7], atol=1e-19)
    assert seen["t"] == 2.5
    assert_allclose(seen["q"], state[:4])
    assert_allclose(seen["omega"], state[4:])


@pytest.mark.parametrize("seed", range(6))
@pytest.mark.parametrize("forced", [False, True])
def test_instantaneous_energy_and_inertial_momentum_balance(seed, forced):
    rng = np.random.default_rng(seed)
    state = np.r_[normalize(rng.normal(size=4)), rng.normal(size=3)]
    config = fixture_config()
    inertia = np.array([[2.0, 0.2, 0.1], [0.2, 3.0, 0.3], [0.1, 0.3, 4.0]])
    config["inertia"] = inertia
    if forced:
        config["test_dipole"] = [0.1, -0.05, 0.02]
    time = 1.5
    derivative = rhs(time, state, config)
    matrix = rotation_matrix(state[:4])
    field, _ = fixture_field(time, config)
    torque = np.cross(config.get("test_dipole", [0, 0, 0]), matrix @ field)
    # Work rate identity is independent of the Euler solver formulation.
    assert_allclose(state[4:] @ inertia @ derivative[4:], state[4:] @ torque,
                    atol=1e-14, rtol=1e-10)

    def inertial_momentum(sample):
        return rotation_matrix(sample[:4]).T @ inertia @ sample[4:]

    # Instantaneous centered difference only, not a time integration test.
    step = 1e-5
    observed = (inertial_momentum(state + step * derivative)
                - inertial_momentum(state - step * derivative)) / (2 * step)
    assert_allclose(observed, matrix.T @ torque, atol=2e-9, rtol=1e-5)


def test_callbacks_are_reevaluated_at_each_requested_time_and_state():
    calls = []

    def field(t, config):
        calls.append(("field", t))
        return fixture_field(t, config)

    def control(t, q, omega, b_b, db_b_dt, config):
        calls.append(("control", t))
        return fixture_controller(t, q, omega, b_b, db_b_dt, config)

    config = fixture_config()
    config.update(field_model=field, controller=control, test_dipole=[0.1, 0, 0])
    first = rhs(0.0, STATE, config)
    second = rhs(0.5, STATE, config)
    changed_state = STATE.copy()
    changed_state[4:] *= 2
    third = rhs(0.0, changed_state, config)
    again = rhs(0.0, STATE, config)
    assert calls == [("field", 0.0), ("control", 0.0), ("field", 0.5), ("control", 0.5),
                     ("field", 0.0), ("control", 0.0), ("field", 0.0), ("control", 0.0)]
    assert not np.array_equal(first[4:], second[4:])
    assert not np.array_equal(first, third)
    assert_allclose(first, again, atol=0, rtol=0)


def test_rhs_preserves_state_and_configuration_arrays():
    config = fixture_config()
    inertia_before = config["inertia"].copy()
    state = STATE.copy()
    rhs(0, state, config)
    assert_allclose(state, STATE, atol=0, rtol=0)
    assert_allclose(config["inertia"], inertia_before, atol=0, rtol=0)


def test_controller_receives_copies_of_stage_state():
    config = fixture_config()

    def modifying_fixture(t, q, omega, b_b, db_b_dt, config):
        command = fixture_controller(t, q, omega, b_b, db_b_dt, config)
        q[:] = 0
        omega[:] = 0
        b_b[:] = 0
        db_b_dt[:] = 0
        return command

    reference = rhs(0, STATE, config)
    config["controller"] = modifying_fixture
    state = STATE.copy()
    assert_allclose(rhs(0, state, config), reference)
    assert_allclose(state, STATE, atol=0, rtol=0)


def test_unprojected_quaternion_derivative_retains_stage_scale():
    state = STATE.copy()
    state[:4] *= 2
    reference = rhs(0, STATE, fixture_config())
    derivative = rhs(0, state, fixture_config())
    assert_allclose(derivative[:4], 2 * reference[:4], atol=1e-15)
    assert_allclose(derivative[4:], reference[4:], atol=1e-15)


@pytest.mark.parametrize("bad", [
    np.eye(2), np.diag([1, 0, 2]), np.diag([1, -1, 2]),
    [[1, 0.2, 0], [0, 1, 0], [0, 0, 1]],
    np.full((3, 3), np.nan), np.eye(3, dtype=complex) * 1j,
])
def test_invalid_inertia_is_rejected(bad):
    with pytest.raises(ValueError):
        angular_acceleration([0, 0, 0], [0, 0, 0], bad)
    config = fixture_config()
    config["inertia"] = bad
    with pytest.raises(ValueError):
        rhs(0, STATE, config)


@pytest.mark.parametrize("bad", [[1, 0, 0, 0], np.full(7, np.nan), np.ones((7, 1)),
                                 [1, 0, 0, 0, 0, 0, 1j], np.zeros(7)])
def test_invalid_state_or_zero_orientation_is_rejected(bad):
    with pytest.raises(ValueError):
        rhs(0, bad, fixture_config())


@pytest.mark.parametrize("bad", [np.nan, np.inf, 1j, [0], "not a time"])
def test_invalid_time_is_rejected(bad):
    with pytest.raises(ValueError):
        rhs(bad, STATE, fixture_config())


@pytest.mark.parametrize("key", ["inertia", "field_model", "controller"])
def test_missing_configuration_fails_explicitly(key):
    config = fixture_config()
    del config[key]
    with pytest.raises(ValueError, match=key):
        rhs(0, STATE, config)


@pytest.mark.parametrize("key", ["field_model", "controller"])
def test_noncallable_dependency_is_rejected(key):
    config = fixture_config()
    config[key] = None
    with pytest.raises(ValueError, match="callable"):
        rhs(0, STATE, config)


@pytest.mark.parametrize("sample", [None, [1, 2, 3], ([1, 2], [0, 0, 0]),
                                    ([1, 2, 3], [0, np.nan, 0]),
                                    ([1j, 0, 0], [0, 0, 0])])
def test_invalid_field_output_is_rejected(sample):
    config = fixture_config()
    config["field_model"] = lambda t, c: sample
    with pytest.raises(ValueError):
        rhs(0, STATE, config)


@pytest.mark.parametrize("key", ["raw_dipole", "dipole", "torque", "saturated"])
def test_missing_controller_output_is_rejected(key):
    config = fixture_config()

    def incomplete(*args):
        result = fixture_controller(*args)
        del result[key]
        return result

    config["controller"] = incomplete
    with pytest.raises(ValueError, match=key):
        rhs(0, STATE, config)


@pytest.mark.parametrize("key, value", [("dipole", [np.inf, 0, 0]),
                                       ("raw_dipole", [0, 0]),
                                       ("torque", [1, 0, 0]), ("saturated", 1)])
def test_invalid_controller_values_are_rejected(key, value):
    config = fixture_config()

    def incorrect(*args):
        result = fixture_controller(*args)
        result[key] = value
        return result

    config["controller"] = incorrect
    with pytest.raises(ValueError):
        rhs(0, STATE, config)


@pytest.mark.parametrize("which", ["config", "command"])
def test_nonmapping_inputs_are_rejected(which):
    config = fixture_config()
    if which == "config":
        config = None
    else:
        config["controller"] = lambda *args: None
    with pytest.raises(ValueError, match="mapping"):
        rhs(0, STATE, config)


@pytest.mark.parametrize("omega, torque", [([0, 0], [0, 0, 0]),
                                           ([0, 0, 0], [0, np.nan, 0])])
def test_angular_acceleration_validates_inputs(omega, torque):
    with pytest.raises(ValueError):
        angular_acceleration(omega, torque, np.eye(3))
