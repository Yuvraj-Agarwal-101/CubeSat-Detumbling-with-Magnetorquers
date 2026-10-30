"""Metrics on piecewise linear output histories, in SI units.

Equality qualifies as below threshold. Interpolated crossings estimate the
continuous history; grid refinement must independently establish adequacy.
"""
import numpy as np


def _history(t, values):
    t, values = np.asarray(t, float), np.asarray(values, float)
    if (t.ndim != 1 or len(t) < 2 or values.shape[0] != len(t)
            or not np.all(np.isfinite(t)) or not np.all(np.isfinite(values))
            or np.any(np.diff(t) <= 0)):
        raise ValueError("finite histories with strictly increasing times required")
    return t, values


def detumbling_time(t, rate, threshold, hold, deadline):
    """Earliest qualifying hold start; None means right censored at deadline.

    Require coverage from t=0 through deadline. Inspect every output segment,
    including excursions between candidate intervals. No extrapolation.
    """
    t, rate = _history(t, rate)
    if (rate.ndim != 1 or np.any(rate < 0) or threshold <= 0 or hold <= 0
            or not np.isfinite([threshold, hold, deadline]).all()
            or deadline < hold or t[0] != 0 or t[-1] < deadline):
        raise ValueError("invalid rate, metric settings, or deadline coverage")

    end = np.searchsorted(t, deadline)
    rate = np.r_[rate[:end], np.interp(deadline, t, rate)]
    t = np.r_[t[:end], deadline]
    start = None
    for a, b, ra, rb in zip(t[:-1], t[1:], rate[:-1], rate[1:]):
        if ra <= threshold and start is None:
            start = a
        if ra > threshold and rb <= threshold:
            start = a + (b-a)*(ra-threshold)/(ra-rb)
        below_end = b
        if ra <= threshold and rb > threshold:
            below_end = a + (b-a)*(threshold-ra)/(rb-ra)
        if start is not None and below_end - start >= hold:
            return float(start)
        if rb > threshold:
            start = None
    return None


def saturation_fraction(t, raw_norm, limit):
    """Exact time fraction above limit for piecewise linear raw dipole norms."""
    t, raw_norm = _history(t, raw_norm)
    if raw_norm.ndim != 1 or np.any(raw_norm < 0) or not np.isfinite(limit) or limit <= 0:
        raise ValueError("invalid dipole norm or limit")
    total = 0.0
    for dt, a, b in zip(np.diff(t), raw_norm[:-1], raw_norm[1:]):
        if a > limit and b > limit:
            total += dt
        elif (a > limit) != (b > limit):
            total += dt * (max(a,b)-limit)/abs(b-a)
    return float(total/(t[-1]-t[0]))


def compute_metrics(t, states, raw_dipole, dipole, torque, settings, limit):
    t, states = _history(t, states)
    if states.shape != (len(t), 7):
        raise ValueError("states must have shape (N,7)")
    vectors = []
    for x in (raw_dipole, dipole, torque):
        _, x = _history(t, x)
        if x.shape != (len(t), 3):
            raise ValueError("actuator histories must have shape (N,3)")
        vectors.append(np.linalg.norm(x, axis=1))
    raw, commanded, torques = vectors
    if np.any(commanded > limit*(1+1e-10)):
        raise ValueError("command exceeds actuator limit")
    if not np.isclose(t[-1], settings['deadline_s'], rtol=0, atol=1e-9):
        raise ValueError("all cases must finish at the common deadline")
    rate = np.linalg.norm(states[:,4:], axis=1)
    td = detumbling_time(t, rate, settings['threshold_rad_s'],
                         settings['hold_s'], settings['deadline_s'])
    return dict(detumbling_time_s=td, success=td is not None,
                censored=td is None, final_rate_rad_s=float(rate[-1]),
                saturation_fraction=saturation_fraction(t,raw,limit),
                peak_torque_Nm=float(torques.max()),
                dipole_effort_Am2_s=float(np.sum(np.diff(t)*(commanded[:-1]+commanded[1:])/2)),
                max_output_spacing_s=float(np.diff(t).max()),
                crossing_rule='piecewise linear rate norm; equality qualifies')
