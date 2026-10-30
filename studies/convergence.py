"""Run exact solution studies with no external numerical integrator."""
from pathlib import Path
import csv
import json
import platform
import time
import numpy as np
from src.integrators import rk4
from tests.exact_cases import (spherical_rhs, exact_rotation, project_quaternion,
                              quaternion_norm, attitude_error, component_error)

ROOT = Path(__file__).resolve().parents[1]


def run():
    config = json.loads((ROOT/'configs/convergence.json').read_text())
    rows = []
    for name in ('scalar', 'spherical'):
        c = config[name]
        previous = None
        for h in c['step_sizes']:
            started = time.perf_counter()
            if name == 'scalar':
                result = rk4(lambda t, y: t*y, c['y0'], c['t_span'], h)
                error = abs(result.states[-1, 0] - np.exp(c['t_span'][1]**2/2))
                rate_error, comp_error, norm_error = None, None, None
            else:
                y0 = np.r_[c['q0'], c['omega_rad_s']]
                result = rk4(spherical_rhs, y0, c['t_span'], h,
                             projection=project_quaternion, norm_diagnostic=quaternion_norm)
                exact = exact_rotation(c['t_span'][1], y0[:4], y0[4:])
                error = attitude_error(result.states[-1, :4], exact)
                comp_error = component_error(result.states[-1, :4], exact)
                rate_error = np.linalg.norm(result.states[-1, 4:] - y0[4:])
                norm_error = np.max(np.abs(result.preprojection_norm_error))
            row = dict(case=name, step_s=h, error=float(error),
                       order=float(np.log2(previous/error)) if previous and error else None,
                       quaternion_component_error=comp_error, omega_error_rad_s=rate_error,
                       max_preprojection_norm_error=norm_error,
                       rhs_evaluations=result.function_evaluations,
                       runtime_s=time.perf_counter()-started)
            rows.append(row)
            previous = error
    out = ROOT/'data/processed'
    out.mkdir(parents=True, exist_ok=True)
    with (out/'convergence.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    record = dict(kind='exact verification fixtures, not full spacecraft',
                  configuration=config, seed=None, python=platform.python_version(),
                  numpy=np.__version__, results=rows)
    (out/'convergence.json').write_text(json.dumps(record, indent=2))
    print(json.dumps(rows, indent=2))
    return rows


if __name__ == '__main__':
    run()
