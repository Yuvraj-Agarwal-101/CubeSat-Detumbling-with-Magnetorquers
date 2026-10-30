"""Generic classical RK4. No spacecraft equations or external solvers."""
from dataclasses import dataclass
from typing import Callable
import math
import numpy as np


@dataclass(frozen=True)
class IntegrationResult:
    times: np.ndarray
    states: np.ndarray
    preprojection_norm_error: np.ndarray
    function_evaluations: int


def rk4(rhs: Callable, y0, t_span, step_size, *, projection=None,
        norm_diagnostic=None):
    """Integrate rhs(t, y) forward with exactly four calls per completed step.

    states has shape (number of times, state dimension). Callbacks take a copy
    of a state. projection is applied only after completed steps. Diagnostics
    are norm_diagnostic(y)-1 before projection, including the supplied y0.
    Without a diagnostic, this array is NaN. y0 is never silently projected.
    A shortened final step lands exactly on t_span[1]. No dense output.
    """
    start, end = map(float, t_span)
    h = float(step_size)
    if np.iscomplexobj(y0):
        raise ValueError('This solver uses real states; represent a complex mode with two real components')
    y = np.asarray(y0, dtype=float).copy()
    if y.ndim != 1 or not y.size or not np.all(np.isfinite(y)):
        raise ValueError('y0 must be a finite nonempty one dimensional array')
    if not all(map(math.isfinite, (start, end, h))) or h <= 0 or end < start:
        raise ValueError('Require finite times, positive step, and end >= start')

    def checked(value, label):
        if np.iscomplexobj(value):
            raise ValueError(label + ' must return real values')
        value = np.asarray(value, dtype=float)
        if value.shape != y.shape or not np.all(np.isfinite(value)):
            raise ValueError(label + ' returned invalid shape or nonfinite values')
        return value.copy()

    def f(t, state):
        return checked(rhs(t, state.copy()), 'rhs')

    def diagnostic(state):
        value = float(norm_diagnostic(state.copy())) - 1 if norm_diagnostic else np.nan
        if norm_diagnostic and not math.isfinite(value):
            raise ValueError('Nonfinite norm diagnostic')
        return value

    times, states, errors = [start], [y.copy()], [diagnostic(y)]
    t, n = start, 0
    while t < end:
        # Anchor the grid to start rather than accumulating floating point h.
        next_t = min(end, start + (n + 1) * h)
        if next_t <= t:
            raise ValueError('Step too small to advance time')
        endpoint_tolerance = min(8 * np.finfo(float).eps * max(abs(end), abs(next_t), h), 1e-10*h)
        if 0 < end - next_t <= endpoint_tolerance:
            next_t = end
        dt = next_t - t
        if dt <= 0 or t + dt / 2 == t:
            raise ValueError('Step too small to resolve stage times')
        k1 = f(t, y)
        k2 = f(t + dt / 2, y + dt * k1 / 2)
        k3 = f(t + dt / 2, y + dt * k2 / 2)
        k4 = f(next_t, y + dt * k3)
        raw = checked(y + dt * (k1 + 2 * k2 + 2 * k3 + k4) / 6, 'step')
        errors.append(diagnostic(raw))
        y = checked(projection(raw.copy()), 'projection') if projection else raw
        times.append(next_t)
        states.append(y.copy())
        t, n = next_t, n + 1
    return IntegrationResult(np.array(times), np.array(states), np.array(errors), 4 * n)
