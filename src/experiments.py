"""Reproducible common ensembles. No dynamics or time integration here."""
import copy
import hashlib
import itertools
import json
import numpy as np
from src.config import load_config, validate_config, case_summary


def generate_cases(config, grid='pilot'):
    baseline = load_config(config['baseline_path'])
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
        document=copy.deepcopy(baseline)
        document['initial_conditions']={'quaternion':q,'angular_velocity_rad_s':(direction*np.deg2rad(spin)).tolist()}
        document['physical']['orbit']['phase_rad']=phase
        document['physical']['controller']['gain_kg_m2_s']=gain
        document['physical']['controller']['max_dipole_a_m2']=limit
        for path in ('initial_conditions.quaternion','initial_conditions.angular_velocity_rad_s',
                     'physical.orbit.phase_rad','physical.controller.gain_kg_m2_s',
                     'physical.controller.max_dipole_a_m2'):
            document['provenance'][path]={'classification':'project_choice',
                'note':f'Seeded {grid} ensemble or parameter sweep override; seed {config["seed"]}.'}
        document=validate_config(document)
        timing=case_summary(document)
        case = dict(config=copy.deepcopy(document['physical']),document=document,
                    seed=config['seed'], geometry_id=g, spin_deg_s=spin,
                    gain_kg_m2_s=gain, dipole_limit_Am2=limit, field_mode=field,
                    phase_rad=phase, y0=q+(direction*np.deg2rad(spin)).tolist(),
                    metrics=dict(threshold_rad_s=timing['rate_threshold_rad_s'],hold_s=timing['hold_duration_s'],deadline_s=timing['deadline_s']), grid=grid)
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
