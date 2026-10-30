"""Exact solutions, known amplification factors, and grid independent norms."""

import numpy as np
import pytest
from numpy.testing import assert_allclose

from src.numerics.errors import fit_order, quaternion_error, trajectory_norm
from src.numerics.integrators import integrate, rk4, rk4_step
from src.numerics.stability import amplification, jacobian, mode_summary
from src.physics.verification import exact_free_sphere, project_attitude
from src.physics.quaternion import quaternion_derivative


@pytest.mark.parametrize("method, expected", [("euler", 1), ("heun", 2), ("rk4", 4)])
def test_global_convergence_on_exact_decay(method, expected):
    steps = .2 / 2 ** np.arange(4)
    errors = []
    for dt in steps:
        t, u, diagnostics = integrate(lambda u, t: -u, [1.0], 2, dt, method=method)
        errors.append(trajectory_norm(t, u[:, 0] - np.exp(-t)))
        assert diagnostics["rhs_evaluations"] == {"euler": 1, "heun": 2, "rk4": 4}[method] * (len(t) - 1)
    observed, _ = fit_order(steps, errors)
    assert abs(observed - expected) < .12


def test_rk4_scalar_amplification_matches_hand_polynomial():
    for w in [-3.0, -2.0, -.1, .5j, -1 + .2j]:
        initial = np.array([1 + 0j])
        result = rk4_step(lambda u, t: w * u, initial, 0, 1)
        expected = 1 + w + w*w/2 + w*w*w/6 + w*w*w*w/24
        assert_allclose(result, expected, atol=1e-15)


@pytest.mark.parametrize("time_dependent", [False, True])
def test_fourth_order_on_nonlinear_and_time_dependent_exact_problems(time_dependent):
    steps, errors = .1 / 2 ** np.arange(4), []
    if time_dependent:
        f = lambda u, t: t * u
        exact = lambda t: np.exp(t * t / 2)
        initial = [1.0]
    else:
        f = lambda u, t: u * (1 - u)
        exact = lambda t: np.exp(t) / (4 + np.exp(t))
        initial = [.2]
    for dt in steps:
        t, u, _ = rk4(f, initial, 1, dt)
        errors.append(trajectory_norm(t, exact(t) - u[:, 0]))
    assert 3.8 < fit_order(steps, errors)[0] < 4.2


def test_rk4_uses_each_stage_time_and_has_no_initial_projection():
    calls, projections = [], []

    def f(u, t):
        calls.append(t)
        return np.array([t])

    def project(u):
        projections.append(u.copy())
        return u

    t, u, _ = rk4(f, [2.0], 1, 1, project=project)
    assert_allclose(calls, [0, .5, .5, 1])
    assert len(projections) == 1
    assert_allclose(u[:, 0], [2, 2.5])


def test_final_short_step_and_nonzero_initial_time():
    t, u, _ = rk4(lambda u, t: np.ones(1), [5.0], 2, .3, t0=1)
    assert_allclose(t, [1, 1.3, 1.6, 1.9, 2])
    assert_allclose(u[:, 0], 5 + t - 1)


def test_complex_oscillation_and_zero_duration():
    t, u, _ = rk4(lambda u, t: 1j * u, [1 + 0j], 1, .01)
    assert_allclose(u[:, 0], np.exp(1j * t), atol=1e-9)
    t, u, diagnostics = rk4(lambda u, t: -u, [1], 2, .1, t0=2)
    assert_allclose(t, [2])
    assert_allclose(u, [[1]])
    assert diagnostics["rhs_evaluations"] == 0


def test_constant_rate_quaternion_convergence_with_projection():
    omega = np.array([.3, -.2, .4])
    steps, errors = .4 / 2 ** np.arange(4), []
    for dt in steps:
        t, q, diagnostics = rk4(lambda q, t: quaternion_derivative(q, omega),
                               [1, 0, 0, 0], 4, dt,
                               project=lambda q: project_attitude(np.r_[q, omega])[:4])
        exact = exact_free_sphere(t, [1, 0, 0, 0], omega)
        errors.append(trajectory_norm(t, quaternion_error(exact, q)))
        assert_allclose(np.linalg.norm(q, axis=1), 1, atol=3e-16)
        assert np.all(diagnostics["projection_correction_norm"] >= 0)
    assert 3.9 < fit_order(steps, errors)[0] < 4.1


def test_trajectory_norm_does_not_depend_on_sample_count_for_constant_error():
    for n in [3, 10, 101]:
        t = np.linspace(0, 2, n)
        assert_allclose(trajectory_norm(t, np.ones((n, 2))), 2)
    assert_allclose(trajectory_norm([0, .2, 1], np.ones(3) * 1j), 1)


def test_sign_independent_quaternion_error_and_zero_rate_exact_case():
    assert_allclose(quaternion_error([1, 0, 0, 0], [-1, 0, 0, 0]), 0)
    assert_allclose(exact_free_sphere([0, 1, 2], [1, 0, 0, 0], [0, 0, 0]),
                    [[1, 0, 0, 0]] * 3)


def test_centered_logarithmic_fit_recovers_known_power():
    h = np.array([.2, .1, .05, .025])
    order, intercept = fit_order(h, 3 * h ** 4)
    assert_allclose(order, 4, atol=1e-14)
    assert_allclose(intercept, np.log(3), atol=1e-14)


def test_linearization_and_stability_distinguish_neutral_and_growth_modes():
    matrix = np.diag([-1., -1000., 0., .2])
    observed = jacobian(lambda u, t: matrix @ u + t, np.ones(4), .3)
    assert_allclose(observed, matrix, atol=1e-8)
    summary = mode_summary(observed, .01)
    assert summary["zero_modes"] == 1
    assert_allclose(summary["nonzero_timescale_ratio"], 5000, rtol=1e-8)
    assert np.sum(summary["decaying"]) == 2
    assert np.sum(summary["growing"]) == 1
    assert abs(amplification(-2)) < 1
    assert abs(amplification(-3)) > 1


@pytest.mark.parametrize("dt", [0, -1, np.nan, np.inf])
def test_bad_step_rejected(dt):
    with pytest.raises(ValueError):
        rk4(lambda u, t: u, [1], 1, dt)


@pytest.mark.parametrize("f", [lambda u, t: [np.nan], lambda u, t: [1, 2]])
def test_invalid_derivative_output(f):
    with pytest.raises(ValueError):
        rk4(f, [1], 1, .1)


def test_invalid_projection_and_unexpected_complex_derivative():
    with pytest.raises(ValueError):
        rk4(lambda u, t: u, [1], 1, .1, project=lambda u: [1, 2])
    with pytest.raises(ValueError):
        rk4(lambda u, t: 1j * u, [1.0], 1, .1)


@pytest.mark.parametrize("steps, errors", [([1, 1], [1, 2]), ([1, .5], [0, 1]), ([1, .5], [np.nan, 1])])
def test_invalid_order_fit(steps, errors):
    with pytest.raises(ValueError):
        fit_order(steps, errors)
