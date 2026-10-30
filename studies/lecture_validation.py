"""Lecture examples and one step error evidence, independent of flight physics."""
import json
from pathlib import Path
import numpy as np
from src.integrators import rk4
from src.numerical_analysis import frozen_linear_diagnostics

ROOT = Path(__file__).resolve().parents[1]


def run():
    local = []
    previous = None
    for h in [.4, .2, .1, .05, .025]:
        # Exact u'=u, u(0)=1. expm1 avoids subtracting two numbers near one.
        numerical = rk4(lambda t,y:y, [1.], (0,h), h).states[-1,0]
        defect = abs(np.expm1(h)-(numerical-1))
        local.append(dict(step_s=h, one_step_defect=defect, truncation_error_per_time=defect/h,
                          defect_order=None if previous is None else float(np.log2(previous/defect))))
        previous = defect
    matrix = np.array([[-2.,0.],[400.,-2000.]])
    stability = []
    for h in [.001,.0015]:
        result = rk4(lambda t,y:matrix@y, [0.,1.], (0,.03), h)
        stability.append(dict(step_s=h, final_fast_mode=float(result.states[-1,1]),
                              exact_final_fast_mode=float(np.exp(-60)),
                              diagnostics=frozen_linear_diagnostics(matrix,h)))
    record = dict(scope='Lecture verification fixtures, not production CubeSat results',
                  configuration=dict(local_ode='u_prime=u',local_y0=[1.],local_t0=0,
                                     matrix=matrix.tolist(),linear_y0=[0.,1.],linear_t_span=[0,.03],seed=None),
                  local_errors=local, frozen_linear_examples=stability)
    (ROOT/'data/processed/lecture_validation.json').write_text(json.dumps(record,indent=2)+'\n')
    rows = []
    for row in local:
        order = '{}' if row['defect_order'] is None else f"{row['defect_order']:.4f}"
        rows.append(f"{row['step_s']:g} & {row['one_step_defect']:.4e} & {row['truncation_error_per_time']:.4e} & {order} " + chr(92)*2)
    template = (ROOT/'studies/templates/lecture_alignment.tex').read_text()
    text = template.replace('@@TABLE_ROWS@@', chr(10).join(rows))
    (ROOT/'report/sections/lecture_alignment.tex').write_text(text)
    print('Recorded lecture truncation error and stability examples')
    return record


if __name__ == '__main__':
    run()
