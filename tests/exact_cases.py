"""Verification fixtures only. These are not Person 1's spacecraft modules."""
import numpy as np


def multiply(a, b):
    s, v, u, w = a[0], np.asarray(a[1:]), b[0], np.asarray(b[1:])
    return np.r_[s * u - v @ w, s * w + u * v + np.cross(v, w)]


def exact_rotation(t, q0, omega):
    speed = np.linalg.norm(omega)
    if speed == 0:
        return np.asarray(q0).copy()
    half = speed * t / 2
    return multiply(q0, np.r_[np.cos(half), np.asarray(omega) * np.sin(half) / speed])


def spherical_rhs(t, y):
    # Direct component equations, separate from the reference multiplication.
    s, x, yv, z, a, b, c = y
    return np.array([-(x*a+yv*b+z*c)/2,
                     (s*a+yv*c-z*b)/2,
                     (s*b+z*a-x*c)/2,
                     (s*c+x*b-yv*a)/2, 0., 0., 0.])


def project_quaternion(y):
    y = np.asarray(y, dtype=float).copy()
    norm = np.linalg.norm(y[:4])
    if norm == 0:
        raise ValueError('Cannot normalize zero quaternion')
    y[:4] /= norm
    return y


def quaternion_norm(y):
    return np.linalg.norm(y[:4])


def attitude_error(q, exact):
    q = np.asarray(q) / np.linalg.norm(q)
    exact = np.asarray(exact) / np.linalg.norm(exact)
    if q @ exact < 0:
        q = -q
    relative = multiply(np.r_[exact[0], -exact[1:]], q)
    return 2 * np.arctan2(np.linalg.norm(relative[1:]), abs(relative[0]))


def component_error(q, exact):
    return np.linalg.norm(q - exact if q @ exact >= 0 else q + exact)


def rotation_matrix(q):
    s, v = q[0], np.asarray(q[1:])
    x, y, z = v
    skew = np.array([[0, -z, y], [z, 0, -x], [-y, x, 0]])
    return (s*s - v@v) * np.eye(3) + 2*np.outer(v, v) - 2*s*skew
