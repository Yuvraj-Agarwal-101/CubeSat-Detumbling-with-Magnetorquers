"""Continuous normalized B dot feedback with a total dipole norm bound."""
import numpy as np
from .orbit_field import _scalar


def _vector(value, name):
    if np.iscomplexobj(value):
        raise ValueError(name+' must be real')
    vector = np.asarray(value, dtype=float)
    if vector.shape != (3,) or not np.all(np.isfinite(vector)):
        raise ValueError(name+' must be a finite three component vector')
    return vector


def controller(t, q, omega, b_b, db_b_dt, config):
    """dB_B/dt already includes body rotation. Do not subtract it again.

    Gain units are kg m^2/s. Dipole is A m^2 and torque is N m.
    q and omega are unused because the derivative is supplied by dynamics.
    """
    _scalar(t, 'time')
    field, derivative = _vector(b_b, 'field'), _vector(db_b_dt, 'field derivative')
    settings = config['controller_settings']
    if settings['law'] != 'normalized_b_dot' or settings['saturation'] != 'vector_norm':
        raise ValueError('Unsupported controller law or saturation')
    gain = _scalar(settings['gain_kg_m2_s'], 'gain', True)
    limit = _scalar(settings['max_dipole_a_m2'], 'dipole limit', True)
    field_norm = np.linalg.norm(field)
    if not np.isfinite(field_norm) or field_norm <= np.sqrt(np.finfo(float).tiny):
        raise ValueError('Field magnitude is zero or numerically unresolved')
    raw = -gain*(derivative/field_norm)/field_norm
    if not np.all(np.isfinite(raw)):
        raise ValueError('Raw command is outside floating point range')
    magnitude = np.linalg.norm(raw)
    if not np.isfinite(magnitude):
        raise ValueError('Raw command magnitude is outside floating point range')
    saturated = bool(magnitude > limit)
    dipole = raw*(limit/magnitude) if saturated else raw.copy()
    return dict(raw_dipole=raw, dipole=dipole, torque=np.cross(dipole,field), saturated=saturated)
