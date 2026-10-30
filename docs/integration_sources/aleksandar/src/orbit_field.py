"""Analytic circular orbit and rotating tilted dipole, in inertial SI components.

These are the idealized project assumptions, not an epoch specific Earth model.
The derivative includes both spacecraft motion and rotating dipole direction.
"""
import numpy as np


def _scalar(value, name, positive=False):
    if np.iscomplexobj(value) or np.ndim(value) != 0 or isinstance(value, (bool, np.bool_)):
        raise ValueError(name+' must be a real scalar')
    value = float(value)
    if not np.isfinite(value) or (positive and value <= 0):
        raise ValueError(name+' is invalid')
    return value


def circular_orbit(t, config):
    """Return position and velocity using active R3(raan) R1(inclination)."""
    t = _scalar(t, 'time')
    orbit = config['orbit']
    radius = _scalar(orbit['earth_radius_m'], 'Earth radius', True) + _scalar(orbit['altitude_m'], 'altitude')
    if radius <= 0 or orbit['altitude_m'] < 0:
        raise ValueError('Invalid orbital radius or altitude')
    mu = _scalar(orbit['gravitational_parameter_m3_s2'], 'mu', True)
    inclination = _scalar(orbit['inclination_rad'], 'inclination')
    node = _scalar(orbit['raan_rad'], 'node')
    phase = _scalar(orbit['phase_rad'], 'phase')
    n = np.sqrt(mu/radius**3)
    u = n*t + phase
    # Inertial basis for the orbital plane.
    a = np.array([np.cos(node), np.sin(node), 0.])
    b = np.array([-np.sin(node)*np.cos(inclination),
                  np.cos(node)*np.cos(inclination), np.sin(inclination)])
    return radius*(np.cos(u)*a+np.sin(u)*b), radius*n*(-np.sin(u)*a+np.cos(u)*b)


def dipole_axis(t, config):
    t = _scalar(t, 'time')
    magnetic = config['magnetic']
    tilt = _scalar(magnetic['dipole_tilt_rad'], 'dipole tilt')
    rate = _scalar(magnetic['earth_rotation_rate_rad_s'], 'Earth rotation')
    if rate < 0:
        raise ValueError('Earth rotation rate must be nonnegative')
    theta = rate*t+_scalar(magnetic['earth_rotation_phase_rad'], 'Earth phase')
    d = np.array([np.sin(tilt)*np.cos(theta), np.sin(tilt)*np.sin(theta), np.cos(tilt)])
    return d, rate*np.array([-d[1], d[0], 0.])


def field_model(t, config):
    """Return B_I and its total derivative along the prescribed orbit."""
    r, velocity = circular_orbit(t, config)
    radius = np.linalg.norm(r)
    radial, radial_dot = r/radius, velocity/radius
    d, d_dot = dipole_axis(t, config)
    surface = _scalar(config['magnetic']['equatorial_surface_field_t'], 'field scale', True)
    scale = surface*(config['orbit']['earth_radius_m']/radius)**3
    g = d@radial
    g_dot = d_dot@radial+d@radial_dot
    field = scale*(3*g*radial-d)
    derivative = scale*(3*g_dot*radial+3*g*radial_dot-d_dot)
    return field, derivative


def frozen_inertial_field(t, config):
    """Freeze B_I at t=0 while dynamics still rotates it into the body."""
    _scalar(t, 'time')
    return field_model(0., config)[0], np.zeros(3)
