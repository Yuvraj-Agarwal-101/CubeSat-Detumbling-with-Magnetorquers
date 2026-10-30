"""Scalar first Hamilton quaternions for the shared attitude convention.

A quaternion is [s, vx, vy, vz]. The matrix returned by rotation_matrix
maps inertial vector components to body components. For a unit quaternion,
C_BI = (s*s - v dot v) I + 2 outer(v, v) - 2 s skew(v).
Thus [cos(theta/2), 0, 0, sin(theta/2)] maps inertial x to
[cos(theta), -sin(theta), 0] in the body frame.

Hamilton multiplication is used, so C_BI(p * q) = C_BI(q) @ C_BI(p).
Body angular velocity gives q_dot = 0.5 * (q * [0, omega]).
No function mutates its arguments. Only normalization and rotation_matrix
normalize a local copy. In particular, quaternion_derivative preserves the
unprojected intermediate states required by a numerical integrator.
"""

import numpy as np
from ..numerics.algebra import real_array


def _vector(value, size, name):
    """Validate a finite real vector without flattening or discarding data."""
    return real_array(value, (size,), name)


def normalize(q):
    """Return a unit quaternion, retaining its sign; reject the zero vector.

    Scaling before computing the norm avoids unnecessary overflow or
    underflow for finite nonzero inputs with very large or small magnitude.
    """
    q = _vector(q, 4, "q")
    scale = np.max(np.abs(q))
    if scale == 0.0:
        raise ValueError("a zero quaternion has no orientation")
    scaled = q / scale
    return scaled / np.linalg.norm(scaled)


def conjugate(q):
    """Return [s, -v] without normalizing; valid for nonunit quaternions."""
    result = _vector(q, 4, "q").copy()
    result[1:] *= -1.0
    return result


def inverse(q):
    """Return the multiplicative inverse, not merely the conjugate.

    The inverse is conjugate(q) / squared_norm(q). A scaled evaluation
    also supports nonunit quaternions without squaring their full scale.
    """
    q = _vector(q, 4, "q")
    scale = np.max(np.abs(q))
    if scale == 0.0:
        raise ValueError("a zero quaternion has no inverse")
    scaled = q / scale
    with np.errstate(over="ignore"):
        result = (conjugate(scaled) / np.dot(scaled, scaled)) / scale
    if not np.all(np.isfinite(result)):
        raise ValueError("quaternion inverse is outside floating point range")
    return result


def multiply(p, q):
    """Return the Hamilton product p times q, with no normalization.

    Its scalar part is ps*qs - pv dot qv. Its vector part is
    ps*qv + qs*pv + pv cross qv. Operand order is significant.
    """
    p = _vector(p, 4, "p")
    q = _vector(q, 4, "q")
    return np.concatenate((
        [p[0] * q[0] - np.dot(p[1:], q[1:])],
        p[0] * q[1:] + q[0] * p[1:] + np.cross(p[1:], q[1:]),
    ))


def rotation_matrix(q):
    """Return C_BI for the orientation encoded by any finite nonzero q.

    A local unit copy gives a proper rotation even when the input carries
    integration norm drift. The caller's state is never projected here.
    Projection of the integrated quaternion remains the integrator's job.
    """
    unit = normalize(q)
    s, x, y, z = unit
    v = unit[1:]
    skew = np.array([[0.0, -z, y], [z, 0.0, -x], [-y, x, 0.0]])
    return ((s * s - np.dot(v, v)) * np.eye(3)
            + 2.0 * np.outer(v, v) - 2.0 * s * skew)


def quaternion_derivative(q, omega):
    """Return q_dot for body angular velocity omega in radians per second.

    s_dot = -0.5 * (v dot omega)
    v_dot = 0.5 * (s * omega + v cross omega)

    q is not normalized. The kinematic equation remains linear in the
    quaternion, including intermediate numerical integration states.
    """
    q = _vector(q, 4, "q")
    omega = _vector(omega, 3, "omega")
    return 0.5 * np.concatenate((
        [-np.dot(q[1:], omega)],
        q[0] * omega + np.cross(q[1:], omega),
    ))
