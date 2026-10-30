"""Reproducible common ensembles. No dynamics or time integration here."""
import copy
import hashlib
import itertools
import json
import numpy as np


def generate_cases(config, grid='pilot'):
    levels = config['grids'][grid]
    rng = np.random.default_rng(config['seed'])
    geometries = []
    for _ in range(levels['geometries']):
        q = rng.normal(size=4); q /= np.linalg.norm(q)
        direction = rng.normal(size=3); direction /= np.linalg.norm(direction)
        geometries.append((q.tolist(), direction, float(rng.uniform(0,2*np.pi))))
    for spin, gain, limit, field, g in itertools.product(
            levels['spin_deg_s'], levels['gain_kg_m2_s'], levels['dipole_limit_Am2'],
            config['field_modes'], range(len(geometries))):
        q, direction, phase = geometries[g]
        case = dict(config=copy.deepcopy(config['physical']),
                    seed=config['seed'], geometry_id=g, spin_deg_s=spin,
                    gain_kg_m2_s=gain, dipole_limit_Am2=limit, field_mode=field,
                    phase_rad=phase, y0=q+(direction*np.deg2rad(spin)).tolist(),
                    metrics=copy.deepcopy(config['metrics']), grid=grid)
        case['case_id']=hashlib.sha256(json.dumps(case,sort_keys=True).encode()).hexdigest()[:16]
        yield case


def summarize(records):
    """Invalid simulations stay visible and never become deadline failures."""
    invalid = [r for r in records if r['status'] != 'valid']
    valid = [r for r in records if r['status'] == 'valid']
    times = [r['metrics']['detumbling_time_s'] for r in valid if r['metrics']['success']]
    n = len(valid)
    return dict(total=len(records), valid=n, invalid=len(invalid), successes=len(times),
                success_fraction=None if not n else len(times)/n,
                conditional_median_time_s=None if not times else float(np.median(times)),
                censored=n-len(times))
