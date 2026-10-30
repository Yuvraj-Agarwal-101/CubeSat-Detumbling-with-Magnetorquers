"""Basic array checks and symmetric positive definite matrices."""

import numpy as np


def real_array(value, shape, name):
    if np.iscomplexobj(value):
        raise ValueError(f"{name} must be real")
    try:
        array = np.asarray(value, dtype=float)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be a real array of shape {shape}") from exc
    if array.shape != shape or not np.all(np.isfinite(array)):
        raise ValueError(f"{name} must be finite with shape {shape}")
    return array


def positive_definite_matrix(value, name="inertia"):
    """Validate the matrix defining a positive energy inner product."""
    matrix = real_array(value, (3, 3), name)
    if not np.allclose(matrix, matrix.T, rtol=1e-12, atol=0):
        raise ValueError(f"{name} must be symmetric")
    matrix = 0.5 * matrix + 0.5 * matrix.T
    if np.min(np.linalg.eigvalsh(matrix)) <= 0:
        raise ValueError(f"{name} must be positive definite")
    return matrix
