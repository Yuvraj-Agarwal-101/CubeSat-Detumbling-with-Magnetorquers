"""Time first compatibility API for the shared numerical implementation."""
from dataclasses import dataclass
import math
import numpy as np
from .numerics.integrators import integrate


@dataclass(frozen=True)
class IntegrationResult:
    times: np.ndarray
    states: np.ndarray
    preprojection_norm_error: np.ndarray
    function_evaluations: int


def rk4(rhs, y0, t_span, step_size, *, projection=None, norm_diagnostic=None):
    """Use common RK4 stages while retaining the team's time first interface.

    Signed diagnostics are norm_diagnostic(raw_state) minus one, before
    projection and at the supplied initial state. Only the numerical layer
    implements stage arithmetic. Inputs are never silently projected.
    """
    if np.iscomplexobj(y0):
        raise ValueError("this compatibility API requires real initial data")
    initial = np.asarray(y0, dtype=float)
    if initial.ndim != 1 or not initial.size or not np.all(np.isfinite(initial)):
        raise ValueError("y0 must be a finite nonempty one dimensional array")
    start, end = map(float, t_span)
    if not callable(rhs) or (projection is not None and not callable(projection)):
        raise ValueError("callbacks must be callable")
    if norm_diagnostic is not None and not callable(norm_diagnostic):
        raise ValueError("norm diagnostic must be callable")

    def diagnostic(state):
        value = float(norm_diagnostic(state.copy())) - 1 if norm_diagnostic else np.nan
        if norm_diagnostic and not math.isfinite(value):
            raise ValueError("Nonfinite norm diagnostic")
        return value

    errors = [diagnostic(initial)]

    def completed_step(raw):
        errors.append(diagnostic(raw))
        return raw if projection is None else projection(raw.copy())

    times, states, metadata = integrate(
        lambda u, t: rhs(t, u), initial, end, step_size, t0=start,
        method="rk4", project=completed_step)
    return IntegrationResult(times, states, np.asarray(errors), metadata["rhs_evaluations"])
