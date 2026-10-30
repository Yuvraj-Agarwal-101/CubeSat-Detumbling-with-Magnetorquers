"""Exact special cases and geometric diagnostics for independent checks."""

import numpy as np
from .quaternion import multiply, normalize


def exact_free_sphere(times, q0, omega):
    """Exact attitude for zero torque and spherical inertia."""
    times, omega = np.asarray(times), np.asarray(omega)
    rate = np.linalg.norm(omega)
    q0 = normalize(q0)
    if rate == 0:
        return np.tile(q0, (len(times), 1))
    return np.array([multiply(q0, np.r_[np.cos(rate * t / 2),
                                      omega / rate * np.sin(rate * t / 2)]) for t in times])


def project_attitude(state):
    """Return a copy with its quaternion normalized after a complete step."""
    result = np.array(state, copy=True)
    result[:4] = normalize(result[:4])
    return result
