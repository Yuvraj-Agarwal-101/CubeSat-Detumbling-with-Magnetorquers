"""Euler rigid body dynamics and the seven component attitude RHS.

State order is [s, vx, vy, vz, wx, wy, wz]. Rates use radians per second.
The passive C_BI maps inertial vector components to body components.

The config mapping must supply these entries.

    inertia
        A real symmetric positive definite 3 by 3 inertia in kg m^2.
    field_model
        A pure callable field_model(t, config) returning (B_I, dB_I_dt).
        Both are shape (3,), in tesla and tesla per second. The derivative
        must include motion along the prescribed orbit and Earth rotation.
    controller
        A pure callable controller(t, q, omega, B_B, dB_B_dt, config).
        It returns a mapping with raw_dipole, dipole, torque, saturated.
        Dipoles are body vectors in A m^2, torque is a body vector in N m,
        and saturated is a boolean. Its torque must equal dipole cross B_B.

Other config entries are owned by the field and controller modules.
Missing callbacks are an explicit error. No default magnetic model or
controller is invented here. Fixtures in the tests are not flight models.
This module advances no time steps and retains no history between calls.
"""

from collections.abc import Mapping

import numpy as np

from .quaternion import quaternion_derivative, rotation_matrix


def _real_array(value, shape, name):
    """Require a finite real array of the stated shape."""
    if np.iscomplexobj(value):
        raise ValueError(f"{name} must be real")
    try:
        array = np.asarray(value, dtype=float)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be a real array of shape {shape}") from exc
    if array.shape != shape:
        raise ValueError(f"{name} must have shape {shape}")
    if not np.all(np.isfinite(array)):
        raise ValueError(f"{name} must contain only finite values")
    return array


def _inertia(value):
    matrix = _real_array(value, (3, 3), "inertia")
    if not np.allclose(matrix, matrix.T, rtol=1e-12, atol=0.0):
        raise ValueError("inertia must be symmetric")
    # Use the symmetric part for roundoff level asymmetry accepted above.
    matrix = 0.5 * matrix + 0.5 * matrix.T
    try:
        np.linalg.cholesky(matrix)
    except np.linalg.LinAlgError as exc:
        raise ValueError("inertia must be positive definite") from exc
    return matrix


def _acceleration(omega, torque, inertia):
    # Solve the linear system instead of explicitly computing an inverse.
    return np.linalg.solve(inertia, torque - np.cross(omega, inertia @ omega))


def angular_acceleration(omega, torque, inertia):
    """Return Euler angular acceleration in body components, in rad/s^2.

    inertia @ omega_dot + omega cross (inertia @ omega) = torque.
    Full symmetric positive definite tensors are supported, not only
    diagonal inertia. This utility is independent of field and control.
    """
    omega = _real_array(omega, (3,), "omega")
    torque = _real_array(torque, (3,), "torque")
    return _acceleration(omega, torque, _inertia(inertia))


def rhs(t, y, config):
    """Return seven derivatives evaluated at exactly this time and state.

    Each call reevaluates field and control. In particular, a Runge Kutta
    caller must invoke this function with every stage's time and state.
    dB_B_dt = C_BI @ dB_I_dt - omega cross B_B.

    Quaternion kinematics use the unprojected state. Only rotation_matrix
    uses a normalized local copy for the field orientation. State projection
    after completed integration steps belongs to the integrator owner.

    Controller inputs are copies. Callbacks must not mutate config, retain
    history, or implement their own time advancement. Reported torque is
    checked against dipole cross B_B with rtol 1e-12 and atol 1e-18 N m.
    The actual acceleration uses the cross product torque.
    """
    if np.iscomplexobj(t) or np.ndim(t) != 0:
        raise ValueError("t must be a finite real scalar")
    try:
        time = float(t)
    except (TypeError, ValueError) as exc:
        raise ValueError("t must be a finite real scalar") from exc
    if not np.isfinite(time):
        raise ValueError("t must be a finite real scalar")
    state = _real_array(y, (7,), "y")
    if not isinstance(config, Mapping):
        raise ValueError("config must be a mapping")
    for key in ("inertia", "field_model", "controller"):
        if key not in config:
            raise ValueError(f"config must provide {key}")
    inertia = _inertia(config["inertia"])
    field_model, controller = config["field_model"], config["controller"]
    if not callable(field_model) or not callable(controller):
        raise ValueError("field_model and controller must be callable")

    q, omega = state[:4], state[4:]
    c_bi = rotation_matrix(q)
    sample = field_model(time, config)
    if not isinstance(sample, (tuple, list)) or len(sample) != 2:
        raise ValueError("field_model must return (B_I, dB_I_dt)")
    b_i = _real_array(sample[0], (3,), "B_I")
    db_i_dt = _real_array(sample[1], (3,), "dB_I_dt")
    b_b = c_bi @ b_i
    db_b_dt = c_bi @ db_i_dt - np.cross(omega, b_b)
    command = controller(time, q.copy(), omega.copy(), b_b.copy(), db_b_dt.copy(), config)
    if not isinstance(command, Mapping):
        raise ValueError("controller must return a mapping")
    for key in ("raw_dipole", "dipole", "torque", "saturated"):
        if key not in command:
            raise ValueError(f"controller must return {key}")
    _real_array(command["raw_dipole"], (3,), "raw_dipole")
    dipole = _real_array(command["dipole"], (3,), "dipole")
    reported_torque = _real_array(command["torque"], (3,), "controller torque")
    if not isinstance(command["saturated"], (bool, np.bool_)):
        raise ValueError("saturated must be a boolean")
    torque = np.cross(dipole, b_b)
    if not np.allclose(reported_torque, torque, rtol=1e-12, atol=1e-18):
        raise ValueError("controller torque must equal dipole cross B_B")
    derivative = np.concatenate((
        quaternion_derivative(q, omega),
        _acceleration(omega, torque, inertia),
    ))
    if not np.all(np.isfinite(derivative)):
        raise ValueError("state derivative is outside floating point range")
    return derivative
