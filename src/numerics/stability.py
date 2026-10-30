"""Amplification factors and local linearization; no global stability claim."""

import numpy as np


def amplification(w, method="rk4"):
    w = np.asarray(w)
    if method == "euler":
        return 1 + w
    if method == "heun":
        return 1 + w + w ** 2 / 2
    if method == "rk4":
        return 1 + w + w ** 2 / 2 + w ** 3 / 6 + w ** 4 / 24
    raise ValueError("method must be euler, heun, or rk4")


def jacobian(f, u, t, relative_step=1e-5):
    """Centered finite differences at one state; avoid nonsmooth switches."""
    u = np.asarray(u, dtype=float)
    if u.ndim != 1 or not np.all(np.isfinite(u)) or relative_step <= 0 or not np.isfinite(relative_step):
        raise ValueError("finite vector and positive perturbation size required")
    matrix = np.empty((u.size, u.size))
    for j in range(u.size):
        perturbation = np.zeros_like(u)
        perturbation[j] = relative_step * max(1.0, abs(u[j]))
        plus, minus = np.asarray(f(u + perturbation, t)), np.asarray(f(u - perturbation, t))
        if np.iscomplexobj(plus) or np.iscomplexobj(minus):
            raise ValueError("real linearization requires a real derivative")
        if plus.shape != u.shape or minus.shape != u.shape:
            raise ValueError("derivative shape must match state")
        matrix[:, j] = (plus - minus) / (2 * perturbation[j])
    if not np.all(np.isfinite(matrix)):
        raise ValueError("nonfinite Jacobian")
    return matrix


def mode_summary(matrix, dt, method="rk4"):
    """Separate decay, neutral modes, and physical growth before interpreting R."""
    matrix = np.asarray(matrix)
    if matrix.ndim != 2 or matrix.size == 0 or matrix.shape[0] != matrix.shape[1] or not np.all(np.isfinite(matrix)):
        raise ValueError("finite square matrix required")
    if not np.isfinite(dt) or dt <= 0:
        raise ValueError("positive finite dt required")
    values = np.linalg.eigvals(matrix)
    tolerance = 100 * np.finfo(float).eps * max(1.0, np.max(np.abs(values)))
    nonzero = np.abs(values) > tolerance
    magnitudes = np.abs(values[nonzero])
    return {"eigenvalues": values, "amplification_magnitudes": np.abs(amplification(dt * values, method)),
            "decaying": values.real < -tolerance, "growing": values.real > tolerance,
            "zero_modes": int(np.sum(~nonzero)),
            "nonzero_timescale_ratio": None if magnitudes.size == 0 else float(magnitudes.max() / magnitudes.min())}
