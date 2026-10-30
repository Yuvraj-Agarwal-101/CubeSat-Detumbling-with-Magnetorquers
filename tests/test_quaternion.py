"""Independent geometry and kinematic checks, with no time integrator."""

import numpy as np
import pytest
from numpy.testing import assert_allclose

from src.quaternion import (
    conjugate, inverse, multiply, normalize,
    quaternion_derivative, rotation_matrix,
)


IDENTITY = np.array([1.0, 0.0, 0.0, 0.0])


def test_identity_rotation():
    assert_allclose(rotation_matrix(IDENTITY), np.eye(3), atol=1e-15)


@pytest.mark.parametrize("axis, expected", [
    (0, [[1, 0, 0], [0, 0, 1], [0, -1, 0]]),
    (1, [[0, 0, -1], [0, 1, 0], [1, 0, 0]]),
    (2, [[0, 1, 0], [-1, 0, 0], [0, 0, 1]]),
])
def test_known_positive_quarter_turns(axis, expected):
    q = np.zeros(4)
    q[0] = np.sqrt(0.5)
    q[axis + 1] = np.sqrt(0.5)
    assert_allclose(rotation_matrix(q), expected, atol=5e-16)


def test_quarter_turn_maps_inertial_x_to_negative_body_y():
    q = [np.sqrt(0.5), 0, 0, np.sqrt(0.5)]
    assert_allclose(rotation_matrix(q) @ [1, 0, 0], [0, -1, 0], atol=5e-16)


@pytest.mark.parametrize("axis", [0, 1, 2])
def test_half_turn_keeps_axis_and_reverses_perpendicular_components(axis):
    q = np.zeros(4)
    q[axis + 1] = 1
    diagonal = -np.ones(3)
    diagonal[axis] = 1
    assert_allclose(rotation_matrix(q), np.diag(diagonal), atol=1e-15)


def test_rodrigues_geometry_for_oblique_axis():
    axis = np.array([1.0, 2.0, 3.0]) / np.sqrt(14.0)
    angle = 0.7
    q = np.r_[np.cos(angle / 2), axis * np.sin(angle / 2)]
    vector = np.array([0.4, -0.2, 0.8])
    # Independent passive Rodrigues rotation of a vector.
    expected = (vector * np.cos(angle) - np.cross(axis, vector) * np.sin(angle)
                + axis * np.dot(axis, vector) * (1 - np.cos(angle)))
    assert_allclose(rotation_matrix(q) @ vector, expected, atol=1e-15)


def test_multiplication_identity_on_both_sides():
    q = np.array([0.3, 0.4, -0.2, 0.8])
    assert_allclose(multiply(IDENTITY, q), q, atol=1e-15)
    assert_allclose(multiply(q, IDENTITY), q, atol=1e-15)


def test_hamilton_basis_products_and_operand_order():
    i = [0, 1, 0, 0]
    j = [0, 0, 1, 0]
    k = [0, 0, 0, 1]
    assert_allclose(multiply(i, j), k)
    assert_allclose(multiply(j, i), -np.array(k))
    assert_allclose(multiply(i, i), -IDENTITY)


def test_multiplication_preserves_algebraic_scale():
    assert_allclose(multiply([2, 0, 0, 0], [3, 0, 0, 0]), [6, 0, 0, 0])


@pytest.mark.parametrize("seed", range(8))
def test_rotation_group_properties(seed):
    rng = np.random.default_rng(seed)
    q = normalize(rng.normal(size=4))
    p = normalize(rng.normal(size=4))
    matrix = rotation_matrix(q)
    vector = rng.normal(size=3)
    assert_allclose(matrix.T @ matrix, np.eye(3), atol=2e-15)
    assert_allclose(np.linalg.det(matrix), 1.0, atol=2e-15)
    assert_allclose(matrix @ vector @ (matrix @ vector), vector @ vector, atol=3e-15)
    assert_allclose(rotation_matrix(-q), matrix, atol=1e-15)
    assert_allclose(rotation_matrix(conjugate(q)), matrix.T, atol=1e-15)
    assert_allclose(matrix.T @ (matrix @ vector), vector, atol=2e-15)
    assert_allclose(rotation_matrix(multiply(p, q)),
                    matrix @ rotation_matrix(p), atol=2e-15)


@pytest.mark.parametrize("scale", [0.2, 3.0, 1e-200, 1e200])
def test_nonunit_multiplicative_inverse(scale):
    q = scale * np.array([0.4, -0.3, 0.2, 0.1])
    assert_allclose(multiply(q, inverse(q)), IDENTITY, atol=1e-15)
    assert_allclose(multiply(inverse(q), q), IDENTITY, atol=1e-15)
    assert_allclose(rotation_matrix(inverse(q)), rotation_matrix(q).T, atol=1e-15)


@pytest.mark.parametrize("scale", [1.0, -3.0, 1e308, 1e-308])
def test_normalization_across_floating_point_scales(scale):
    q = scale * np.array([1.0, 0.5, -0.5, 0.25])
    result = normalize(q)
    expected = np.sign(scale) * np.array([1, 0.5, -0.5, 0.25]) / 1.25
    assert_allclose(result, expected, atol=1e-15)
    assert_allclose(np.linalg.norm(result), 1.0, atol=1e-15)


def test_rotation_matrix_uses_unit_copy_without_changing_input():
    q = np.array([2.0, 1.0, 0.5, -0.25])
    before = q.copy()
    assert_allclose(rotation_matrix(q), rotation_matrix(normalize(q)), atol=1e-15)
    assert_allclose(q, before, atol=0, rtol=0)


def test_derivative_identity_and_zero_rate():
    omega = np.array([0.2, -0.3, 0.4])
    assert_allclose(quaternion_derivative(IDENTITY, omega), np.r_[0, omega / 2])
    assert_allclose(quaternion_derivative([0.2, 0.1, 0.3, 0.4], [0, 0, 0]), np.zeros(4))


def test_derivative_remains_linear_without_normalizing_stages():
    q = np.array([0.2, -0.1, 0.3, 0.4])
    omega = np.array([0.5, 0.1, -0.2])
    derivative = quaternion_derivative(q, omega)
    assert_allclose(quaternion_derivative(3 * q, omega), 3 * derivative, atol=1e-15)
    assert_allclose(q @ derivative, 0.0, atol=1e-16)


def test_derivative_matches_independent_constant_rate_curve():
    # Exact scalar first curve for initial identity and omega along axis three.
    rate, time = 0.8, 1.1
    half_angle = rate * time / 2
    q = [np.cos(half_angle), 0, 0, np.sin(half_angle)]
    expected = [-(rate / 2) * np.sin(half_angle), 0, 0,
                (rate / 2) * np.cos(half_angle)]
    assert_allclose(quaternion_derivative(q, [0, 0, rate]), expected, atol=1e-15)


def test_derivative_and_passive_matrix_rate_are_consistent():
    # This finite difference is an instantaneous algebraic check, not integration.
    q = normalize([0.7, 0.2, -0.1, 0.3])
    omega = np.array([0.3, -0.2, 0.4])
    dt = 1e-5
    dq = quaternion_derivative(q, omega)
    observed = (rotation_matrix(q + dt * dq) - rotation_matrix(q - dt * dq)) / (2 * dt)
    x, y, z = omega
    skew = np.array([[0, -z, y], [z, 0, -x], [-y, x, 0]])
    assert_allclose(observed, -skew @ rotation_matrix(q), atol=2e-11, rtol=1e-9)


def test_functions_do_not_modify_inputs():
    q = np.array([0.7, 0.2, -0.1, 0.3])
    omega = np.array([0.3, -0.2, 0.4])
    original_q, original_omega = q.copy(), omega.copy()
    normalize(q)
    conjugate(q)
    inverse(q)
    multiply(q, q)
    rotation_matrix(q)
    quaternion_derivative(q, omega)
    assert_allclose(q, original_q, atol=0, rtol=0)
    assert_allclose(omega, original_omega, atol=0, rtol=0)


@pytest.mark.parametrize("bad", [
    [1, 0, 0], [[1, 0, 0, 0]], [np.nan, 0, 0, 0],
    [np.inf, 0, 0, 0], [1j, 0, 0, 0],
])
@pytest.mark.parametrize("function", [normalize, conjugate, inverse, rotation_matrix])
def test_invalid_quaternion_inputs(function, bad):
    with pytest.raises(ValueError):
        function(bad)


@pytest.mark.parametrize("function", [normalize, inverse, rotation_matrix])
def test_zero_orientation_is_rejected(function):
    with pytest.raises(ValueError):
        function(np.zeros(4))


@pytest.mark.parametrize("bad", [[0, 0], [0, np.nan, 0], [0, 1j, 0], [[0, 0, 0]]])
def test_invalid_angular_velocity(bad):
    with pytest.raises(ValueError):
        quaternion_derivative(IDENTITY, bad)


def test_binary_functions_validate_quaternion_arguments():
    with pytest.raises(ValueError):
        multiply([1, 0, 0], IDENTITY)
    with pytest.raises(ValueError):
        multiply(IDENTITY, [1, 0, np.inf, 0])
    with pytest.raises(ValueError):
        quaternion_derivative([1, 0, 0], [0, 0, 0])
