"""Error norms and frozen linear diagnostics from AE 370 Lectures 3, 12, 13."""
import numpy as np


def trajectory_error_norms(times, errors):
    """Separate physical quantities before calling; never mix q and rate units.

    L2 uses time weighted trapezoid quadrature, including a shortened last step.
    Linfinity is the largest sampled Euclidean error, not a continuous bound.
    """
    t, e = np.asarray(times, float), np.asarray(errors, float)
    if t.ndim != 1 or len(t) < 2 or not np.all(np.isfinite(t)) or np.any(np.diff(t) <= 0):
        raise ValueError('Require finite, strictly increasing sample times')
    if e.ndim == 1:
        e = e[:, None]
    if e.ndim != 2 or len(e) != len(t) or not np.all(np.isfinite(e)):
        raise ValueError('Errors must be finite with one row per time')
    squared = np.sum(e*e, axis=1)
    return {'l2_time': float(np.sqrt(np.trapezoid(squared, t))),
            'linfinity_sampled': float(np.sqrt(np.max(squared)))}


def rk4_amplification(z):
    """Unprojected RK4 stability function, including complex eigenvalues."""
    z = np.asarray(z, dtype=complex)
    if not np.all(np.isfinite(z)):
        raise ValueError('Require finite scaled eigenvalues')
    return 1 + z*(1 + z*(.5 + z*(1/6 + z/24)))


def frozen_linear_diagnostics(jacobian, step):
    """A local diagnostic, not a nonlinear or projected stability certificate.

    A nonnormal or time varying system can amplify errors despite eigenvalues
    inside the region. Zero modes are counted separately from a stiffness ratio.
    """
    matrix = np.asarray(jacobian, dtype=float)
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1] or not matrix.size or not np.all(np.isfinite(matrix)):
        raise ValueError('Require a finite square Jacobian')
    if not np.isfinite(step) or step <= 0:
        raise ValueError('Require a finite positive step')
    eigenvalues = np.linalg.eigvals(matrix)
    tolerance = 1e-12*max(1., float(np.max(abs(eigenvalues))))
    magnitudes = abs(eigenvalues)
    nonzero = magnitudes[magnitudes > tolerance]
    decay = eigenvalues.real < -tolerance
    factors = abs(rk4_amplification(step*eigenvalues))
    return dict(eigenvalues_real=eigenvalues.real.tolist(), eigenvalues_imag=eigenvalues.imag.tolist(),
                amplification_moduli=factors.tolist(),
                neutral_modes=int(np.sum(magnitudes <= tolerance)),
                positive_real_modes=int(np.sum(eigenvalues.real > tolerance)),
                nonzero_mode_ratio=float(max(nonzero)/min(nonzero)) if len(nonzero) else None,
                decaying_modes_outside_region=int(np.sum(decay & (factors >= 1))))
