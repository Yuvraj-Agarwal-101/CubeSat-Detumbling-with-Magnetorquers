"""Full model refinement driver. Requires teammates' real model via an adapter.

The local metrics are screening definitions for review by Person 4. They use
stored endpoints, so threshold detection, peak torque, and saturation fraction
have sampling error. No claim of continuous event localization is made.
"""
import argparse
import importlib
import json
import hashlib
from pathlib import Path
import time
import numpy as np
from src.integrators import rk4
from src.config import validate_config, case_summary

ROOT = Path(__file__).resolve().parents[1]


def sampled_metrics(times, states, torque, saturated, threshold, hold):
    times, states = np.asarray(times), np.asarray(states)
    rates = np.linalg.norm(states[:, 4:7], axis=1)
    first, detumble = None, None
    for i, below in enumerate(rates < threshold):
        if not below:
            first = None
        elif first is None:
            first = i
        if first is not None and times[i]-times[first] >= hold:
            detumble = float(times[first])
            break
    duration = times[-1]-times[0]
    return dict(success=detumble is not None, detumbling_time_s=detumble,
                final_rate_rad_s=float(rates[-1]),
                peak_torque_Nm=float(np.max(np.linalg.norm(torque, axis=1))),
                saturation_fraction=float(np.trapezoid(np.asarray(saturated, dtype=float), times)/duration))


def compare(coarse, fine, tolerances):
    details = {'success': {'pass': coarse['success'] == fine['success']}}
    for key, tol in tolerances.items():
        a, b = coarse[key], fine[key]
        if a is None or b is None:
            details[key] = dict(pass_=a is None and b is None, absolute_difference=None,
                                allowed_difference=None)
            details[key]['pass'] = details[key].pop('pass_')
        else:
            # Use an absolute tolerance only near zero. Else require the relative
            # target, with the absolute tolerance as a floor, not an addition.
            allowed = max(tol['absolute'], tol['relative']*abs(b))
            details[key] = {'pass': abs(a-b) <= allowed,
                            'absolute_difference': abs(a-b), 'allowed_difference': allowed}
    return {'pass': all(item['pass'] for item in details.values()), 'metrics': details}


def select_step(records, steps):
    """Need two consecutive passing refinements for every supplied case."""
    for i in range(len(steps)-2):
        if all(r['comparisons'][i]['pass'] and r['comparisons'][i+1]['pass']
               and r['regime_check_pass'] for r in records):
            if any(r['runs'][i+2]['metrics']['success'] for r in records):
                return steps[i]
    return None


def run(adapter, settings_path=None):
    settings = json.loads(Path(settings_path or ROOT/'configs/timestep_selection.json').read_text())
    steps = settings['step_sizes_s']
    if len(steps) < 3 or any(h <= 0 for h in steps) or not np.allclose(np.array(steps[:-1])/steps[1:], 2):
        raise ValueError('Provide at least three successive positive step halvings')
    if not adapter:
        result = dict(status='pending', reason='No full model adapter supplied',
                      selected_step_s=None, settings=settings)
    else:
        cases = importlib.import_module(adapter).build_cases()
        if {c['regime'] for c in cases} != {'unsaturated', 'saturated'}:
            raise ValueError('Provide unsaturated and saturated cases')
        records = []
        for case in cases:
            if case.get('is_fixture', True):
                raise ValueError('Full model study refuses fixtures or unclassified models')
            # Require serializable provenance before running expensive trajectories.
            # Runtime config contains callable field/controller functions.
            # Record complete parameters and callback import paths separately.
            document = validate_config(case['config_record'])
            summary = case_summary(document)
            json.dumps(case['callback_identifiers'])
            limit = case['config']['controller_settings']['max_dipole_a_m2']
            if limit != document['physical']['controller']['max_dipole_a_m2']:
                raise ValueError('Runtime dipole limit and recorded case must agree')
            if not np.isclose(case['orbital_period_s'], summary['orbital_period_s'], rtol=1e-12):
                raise ValueError('Orbital period must agree with recorded configuration')
            if not np.allclose(case['y0'], summary['initial_state'], rtol=0, atol=1e-12):
                raise ValueError('Initial state must agree with recorded configuration')
            if not np.isclose(settings['rate_threshold_rad_s'], summary['rate_threshold_rad_s'], rtol=1e-12):
                raise ValueError('Refinement threshold must agree with recorded case')
            if settings['hold_duration_s'] != summary['hold_duration_s']:
                raise ValueError('Refinement hold duration must agree with recorded case')
            if not np.isclose(case['t_span'][1]-case['t_span'][0],
                              6*case['orbital_period_s'], rtol=1e-12, atol=1e-8):
                raise ValueError('Each case must run to six orbital periods')
            if case['t_span'][0] != 0 or np.asarray(case['y0']).shape != (7,):
                raise ValueError('Require t0=0 and the shared seven component state')
            if abs(np.linalg.norm(np.asarray(case['y0'])[:4])-1) > 1e-12:
                raise ValueError('Initial quaternion must be normalized')
            runs = []
            for step in steps:
                print(f"Running {case['name']} at h={step:g} s", flush=True)
                began = time.perf_counter()
                def project(y):
                    norm = np.linalg.norm(y[:4])
                    if norm == 0:
                        raise ValueError('Zero quaternion')
                    y[:4] /= norm
                    return y
                sol = rk4(lambda t, y: case['rhs'](t, y, case['config']),
                          case['y0'], case['t_span'], step, projection=project,
                          norm_diagnostic=lambda y: np.linalg.norm(y[:4]))
                diagnostics = [case['diagnostics'](t, y, case['config'])
                               for t, y in zip(sol.times, sol.states)]
                torque = np.array([d['torque'] for d in diagnostics])
                raw = np.array([d['raw_dipole'] for d in diagnostics])
                command = np.array([d['dipole'] for d in diagnostics])
                for values in (torque, raw, command):
                    if values.shape != (len(sol.times), 3) or not np.all(np.isfinite(values)):
                        raise ValueError('Diagnostics must return finite three component vectors')
                sat = np.linalg.norm(raw, axis=1) > limit
                if np.max(np.linalg.norm(command, axis=1)) > limit*(1+1e-10):
                    raise ValueError('Commanded dipole exceeds vector norm bound')
                metric = sampled_metrics(sol.times, sol.states, torque, sat,
                                         settings['rate_threshold_rad_s'], settings['hold_duration_s'])
                metric['dipole_effort_A_m2_s'] = float(np.trapezoid(np.linalg.norm(command, axis=1), sol.times))
                runs.append(dict(step_s=step, metrics=metric, runtime_s=time.perf_counter()-began,
                                 max_preprojection_norm_error=float(np.max(np.abs(sol.preprojection_norm_error))),
                                 rhs_evaluations=sol.function_evaluations))
                print(f"Completed {case['name']} h={step:g}: {metric}", flush=True)
            regimes = [r['metrics']['saturation_fraction'] for r in runs]
            regime_ok = all(f == 0 for f in regimes) if case['regime']=='unsaturated' else all(f > 0 for f in regimes)
            records.append(dict(name=case['name'], regime=case['regime'], config=case['config_record'],
                                y0=np.asarray(case['y0']).tolist(), t_span=case['t_span'],
                                seed=case['seed'], orbital_period_s=case['orbital_period_s'],
                                callback_identifiers=case['callback_identifiers'],
                                intermediate_quaternion_policy=case['intermediate_quaternion_policy'],
                                regime_check_pass=regime_ok, runs=runs,
                                comparisons=[compare(a['metrics'], b['metrics'], settings['tolerances'])
                                             for a,b in zip(runs[:-1], runs[1:])]))
        selected = select_step(records, steps)
        result = dict(status='screening complete, team review required' if selected else 'further refinement or cases required',
                      adapter=adapter, settings=settings, cases=records, selected_step_s=selected,
                      limitation='Sampled events can miss intervening excursions and narrow saturation or torque peaks. Independent physics verification and team approval remain necessary.')
        result['source_hashes']={name:hashlib.sha256((ROOT/name).read_bytes().replace(b'\r\n',b'\n')).hexdigest()
                                for name in ['src/orbit_field.py','src/controller.py','team_adapter.py',
                                             'src/dynamics.py','src/integrators.py'] if (ROOT/name).exists()}
    out = ROOT/'data/processed/timestep_selection.json'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--adapter', help='Importable module providing build_cases()')
    parser.add_argument('--settings')
    args = parser.parse_args()
    run(args.adapter, args.settings)
