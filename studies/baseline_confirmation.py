"""Check that the canonical 0.1 A m^2 bound is inactive at every RK4 stage."""
import json
from pathlib import Path
import time
import numpy as np
from src.config import load_config, runtime_config, case_summary, initial_state
from src.controller import controller
from src.orbit_field import field_model
from src.dynamics import rhs
from src.integrators import rk4
from team_adapter import project, diagnostics
from studies.timestep_selection import sampled_metrics

ROOT=Path(__file__).resolve().parents[1]


def compare_reference(metric,reference):
    # Independent projection implementations can differ in the last bits.
    # This roundoff check is far tighter than the engineering tolerances.
    return all(metric[key]==reference[key] if isinstance(metric[key],bool) or metric[key] is None
               else np.isclose(metric[key],reference[key],rtol=1e-10,atol=1e-12)
               for key in metric)


def main():
    document=load_config();maximum=0.;calls=0
    def observed_controller(*args):
        nonlocal maximum,calls
        value=controller(*args)
        maximum=max(maximum,float(np.linalg.norm(value['raw_dipole'])))
        calls+=1
        return value
    config=runtime_config(document,field_model=field_model,controller=observed_controller)
    original=json.loads((ROOT/'data/processed/timestep_selection.json').read_text())
    step=original['selected_step_s']
    if step is None:
        raise ValueError('Select a refined step before baseline confirmation')
    timing=case_summary(document);began=time.perf_counter()
    sol=rk4(lambda t,y:rhs(t,y,config),initial_state(document),(0,timing['deadline_s']),step,
            projection=project,norm_diagnostic=lambda y:np.linalg.norm(y[:4]))
    samples=[diagnostics(t,y,config) for t,y in zip(sol.times,sol.states)]
    raw=np.array([v['raw_dipole'] for v in samples]);torque=np.array([v['torque'] for v in samples])
    metric=sampled_metrics(sol.times,sol.states,torque,np.linalg.norm(raw,axis=1)>.1,
                           timing['rate_threshold_rad_s'],timing['hold_duration_s'])
    case=next(c for c in original['cases'] if c['name']=='unsaturated')
    reference=next(r for r in case['runs'] if r['step_s']==step)['metrics']
    match=compare_reference(metric,reference)
    result=dict(configuration=document,step_s=step,metrics=metric,runtime_s=time.perf_counter()-began,
                max_preprojection_norm_error=float(np.max(np.abs(sol.preprojection_norm_error))),
                max_projected_norm_error=float(np.max(np.abs(np.linalg.norm(sol.states[:,:4],axis=1)-1))),
                max_raw_dipole_at_all_stages_A_m2=maximum,controller_stage_calls=calls,
                bound_inactive_at_all_stages=maximum<.1,reference_unsaturated_metrics_agree=bool(match),
                reference_roundoff_tolerance=dict(relative=1e-10,absolute=1e-12),
                explanation='The observer does not alter commands. The inactive bound gives the same RHS. Different norm implementations in the two projection callbacks can change the last floating point bits.')
    folder=ROOT/'data/processed/production_validation';folder.mkdir(exist_ok=True)
    (folder/'baseline.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2),flush=True)
    if not match or maximum>=.1:
        raise RuntimeError('Baseline is not equivalent to the unsaturated verification case')


if __name__=='__main__':
    main()
