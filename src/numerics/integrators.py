"""Explicit one step methods for u_dot = f(u, t).

All time advancement is written here. The state first callback convention
is independent of spacecraft physics. To integrate the existing model use
f = lambda u, t: rhs(t, u, runtime). No library IVP solver is called.
"""

import math
import numpy as np


def _evaluate(f, u, t):
    slope = np.asarray(f(u.copy(), t))
    if slope.shape != u.shape or not np.all(np.isfinite(slope)):
        raise ValueError("derivative must be finite and match the state shape")
    return slope


def euler_step(f, u, t, dt):
    return u + dt * _evaluate(f, u, t)


def heun_step(f, u, t, dt):
    y1 = _evaluate(f, u, t)
    y2 = _evaluate(f, u + dt * y1, t + dt)
    return u + 0.5 * dt * (y1 + y2)


def rk4_step(f, u, t, dt):
    y1 = _evaluate(f, u, t)
    y2 = _evaluate(f, u + 0.5 * dt * y1, t + 0.5 * dt)
    y3 = _evaluate(f, u + 0.5 * dt * y2, t + 0.5 * dt)
    y4 = _evaluate(f, u + dt * y3, t + dt)
    return u + dt * (y1 + 2 * y2 + 2 * y3 + y4) / 6


STEPS = {"euler": (euler_step, 1), "heun": (heun_step, 2), "rk4": (rk4_step, 4)}


def integrate(f, u0, t_final, dt, *, t0=0.0, method="rk4", project=None):
    """Return times, states, and projection diagnostics.

    All interior steps use dt. The last step is shortened to end exactly
    at t_final. Projection, if provided, is applied only after a completed
    step. Its Euclidean correction norm is recorded before replacement.
    For quaternion only normalization that norm is abs(norm(q_raw) - 1).
    The initial value is not silently projected.
    """
    if not callable(f) or (project is not None and not callable(project)):
        raise ValueError("f and any projection must be callable")
    if method not in STEPS:
        raise ValueError("method must be euler, heun, or rk4")
    if not all(np.ndim(x) == 0 and not np.iscomplexobj(x) for x in (t0, t_final, dt)):
        raise ValueError("times and dt must be real scalars")
    t0, t_final, dt = float(t0), float(t_final), float(dt)
    if not all(math.isfinite(x) for x in (t0, t_final, dt)) or dt <= 0 or t_final < t0:
        raise ValueError("finite times with t_final at least t0 and positive dt are required")
    u0 = np.atleast_1d(np.asarray(u0))
    if u0.ndim != 1 or not np.all(np.isfinite(u0)) or u0.size == 0:
        raise ValueError("initial state must be a finite nonempty vector")
    dtype = np.result_type(u0.dtype, float)
    if t_final == t0:
        return np.array([t0]), u0.astype(dtype)[None, :], {
            "rhs_evaluations": 0, "projection_correction_norm": np.zeros(1)}
    if t0 + dt == t0:
        raise ValueError("dt cannot advance the time at this floating point scale")
    ratio = (t_final - t0) / dt
    if not math.isfinite(ratio):
        raise ValueError("requested number of steps is outside floating point range")
    nearest = round(ratio)
    n = int(nearest if abs(ratio - nearest) <= 16 * np.finfo(float).eps * max(1, ratio)
            else math.ceil(ratio))
    n = max(1, n)
    times = t0 + dt * np.arange(n + 1)
    times[-1] = t_final
    if not np.all(np.diff(times) > 0):
        raise ValueError("time grid must be strictly increasing")
    states = np.empty((n + 1, u0.size), dtype=dtype)
    states[0] = u0
    corrections = np.zeros(n + 1)
    step, stages = STEPS[method]
    for k in range(n):
        if method == "rk4" and times[k] + (times[k + 1] - times[k]) / 2 == times[k]:
            raise ValueError("step too small to resolve intermediate stage times")
        raw = step(f, states[k], times[k], times[k + 1] - times[k])
        if not np.all(np.isfinite(raw)):
            raise ValueError("time step produced nonfinite state")
        if np.iscomplexobj(raw) and not np.issubdtype(dtype, np.complexfloating):
            raise ValueError("use complex initial data for a complex IVP")
        corrected = raw if project is None else np.asarray(project(raw.copy()))
        if corrected.shape != raw.shape or not np.all(np.isfinite(corrected)):
            raise ValueError("projection must return a finite state of unchanged shape")
        if np.iscomplexobj(corrected) and not np.issubdtype(dtype, np.complexfloating):
            raise ValueError("projection cannot introduce complex state")
        corrections[k + 1] = np.linalg.norm(corrected - raw)
        states[k + 1] = corrected
    return times, states, {"rhs_evaluations": stages * n,
                           "projection_correction_norm": corrections}


def rk4(f, u0, t_final, dt, **kwargs):
    return integrate(f, u0, t_final, dt, method="rk4", **kwargs)
