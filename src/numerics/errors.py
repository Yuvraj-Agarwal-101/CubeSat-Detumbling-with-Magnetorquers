"""Inner product error measures and a linear fit of logarithmic errors."""

import numpy as np


def trajectory_norm(times, errors):
    """Trapezoidal approximation of sqrt(integral ||error(t)||_2^2 dt).

    Time weights prevent a longer sample vector from changing the norm
    merely because the grid has been refined. Complex values use conjugacy.
    """
    times = np.asarray(times, dtype=float)
    errors = np.asarray(errors)
    if times.ndim != 1 or len(times) < 2 or errors.ndim == 0 or errors.shape[0] != len(times):
        raise ValueError("errors must match a time grid with at least two points")
    if not np.all(np.isfinite(times)) or not np.all(np.diff(times) > 0) or not np.all(np.isfinite(errors)):
        raise ValueError("finite errors and a strictly increasing grid are required")
    squared = np.abs(errors) ** 2
    if errors.ndim > 1:
        squared = squared.reshape(len(times), -1).sum(axis=1)
    return np.sqrt(np.sum(np.diff(times) * (squared[1:] + squared[:-1]) / 2))


def quaternion_error(exact, numerical):
    """Sign independent Euclidean quaternion error; use unit inputs."""
    exact, numerical = np.asarray(exact), np.asarray(numerical)
    if exact.shape != numerical.shape or exact.ndim < 1 or exact.shape[-1] != 4:
        raise ValueError("matching quaternion arrays ending in four components are required")
    return np.minimum(np.linalg.norm(exact - numerical, axis=-1),
                      np.linalg.norm(exact + numerical, axis=-1))


def fit_order(step_sizes, errors):
    """Least squares fit log(error) = intercept + order log(dt).

    Centering log(dt) makes the constant and linear columns orthogonal
    under the discrete inner product. The slope is one projection ratio.
    """
    h, e = np.asarray(step_sizes, dtype=float), np.asarray(errors, dtype=float)
    if h.ndim != 1 or e.shape != h.shape or h.size < 2:
        raise ValueError("matching vectors with at least two entries are required")
    if not np.all(np.isfinite(h)) or not np.all(np.isfinite(e)) or np.any(h <= 0) or np.any(e <= 0):
        raise ValueError("fit requires finite positive steps and errors")
    x, y = np.log(h), np.log(e)
    centered = x - x.mean()
    denominator = centered @ centered
    if denominator == 0:
        raise ValueError("step sizes must vary")
    order = (centered @ (y - y.mean())) / denominator
    return float(order), float(y.mean() - order * x.mean())
