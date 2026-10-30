"""Confirm the remaining RK4 refinement and independently audit output sampling.

Reuse recorded coarser simulations only when their physics hashes match.
Quarter-second runs use the same scratch RK4 and full six-orbit deadline.
"""
from concurrent.futures import ProcessPoolExecutor
import hashlib
import json
from pathlib import Path
import time
import numpy as np
from src.config import case_summary
from studies.timestep_selection import sampled_metrics, compare, select_step
from team_adapter import simulate

ROOT=Path(__file__).resolve().parents[1]


def interpolated_hold(t, rate, threshold, hold):
    """Earliest complete hold in a piecewise linear rate interpolant.

    Equality qualifies, matching Person 4's documented convention. This is
    an output interpolation assumption, not a bound on the continuous ODE.
    """
    start=None
    for i in range(len(t)-1):
        a,b=float(t[i]),float(t[i+1]); x,y=rate[i],rate[i+1]
        if x>threshold and y>threshold:
            start=None
            continue
        left=a if x<=threshold else a+(b-a)*(threshold-x)/(y-x)
        right=b if y<=threshold else a+(b-a)*(threshold-x)/(y-x)
        if start is None:
            start=left
        if right-start >= hold:
            return float(start)
        if y>threshold:
            start=None
    return None


def crossing_fraction(t, value, limit):
    """Time above limit for the piecewise linear norm, not a Boolean trapezoid."""
    a,b=value[:-1],value[1:]
    fractions=np.zeros(len(a)); fractions[(a>limit)&(b>limit)]=1
    crossing=(a>limit)!=(b>limit)
    indices=np.flatnonzero(crossing)
    alpha=(limit-a[indices])/(b[indices]-a[indices])
    fractions[indices]=np.where(a[indices]>limit,alpha,1-alpha)
    return float(np.sum(np.diff(t)*fractions)/(t[-1]-t[0]))


def trace_metrics(t, rate, raw, torque, threshold, hold, limit):
    td=interpolated_hold(t,rate,threshold,hold)
    return dict(success=td is not None,detumbling_time_s=td,
                final_rate_rad_s=float(rate[-1]),peak_torque_Nm=float(max(torque)),
                saturation_fraction=crossing_fraction(t,raw,limit))


def run_case(name):
    # Replay the archived case, even after a production solver setting is set
    # in the canonical baseline. Physics hashes are checked in main().
    archived=json.loads((ROOT/'data/processed/timestep_selection.json').read_text())
    saved=next(c for c in archived['cases'] if c['name']==name)
    case=dict(config_record=saved['config'],y0=saved['y0'])
    started=time.perf_counter()
    print('Starting quarter-second confirmation for '+name,flush=True)
    history=simulate(dict(document=case['config_record'],field_mode='orbital',y0=case['y0']),.25)
    t,y=history['t'],history['states']
    raw=np.linalg.norm(history['raw_dipole'],axis=1)
    command=np.linalg.norm(history['dipole'],axis=1)
    torque=np.linalg.norm(history['torque'],axis=1)
    rate=np.linalg.norm(y[:,4:],axis=1)
    timing=case_summary(case['config_record'])
    limit=case['config_record']['physical']['controller']['max_dipole_a_m2']
    metric=sampled_metrics(t,y,history['torque'],raw>limit,timing['rate_threshold_rad_s'],timing['hold_duration_s'])
    metric['dipole_effort_A_m2_s']=float(np.trapezoid(command,t))
    record=dict(step_s=.25,metrics=metric,runtime_s=time.perf_counter()-started,
                max_preprojection_norm_error=float(max(abs(history['preprojection_norm_error']))),
                rhs_evaluations=4*(len(t)-1))
    audits=[]
    for stride in [4,2,1]:
        nodes=np.unique(np.r_[np.arange(0,len(t),stride),len(t)-1])
        audits.append(dict(output_spacing_s=.25*stride,
            metrics=trace_metrics(t[nodes],rate[nodes],raw[nodes],torque[nodes],
                timing['rate_threshold_rad_s'],timing['hold_duration_s'],limit)))
    out=ROOT/'data/processed/production_validation'; out.mkdir(exist_ok=True)
    # Compact scalar histories reproduce the independent output audit exactly.
    np.savez_compressed(out/(name+'_trace.npz'),t=t,rate_rad_s=rate,raw_dipole_norm=raw,
                        dipole_norm=command,torque_norm=torque)
    result=dict(name=name,run=record,output_audit=audits,config=case['config_record'],
                max_raw_dipole_A_m2=float(max(raw)),
                norm_diagnostic_max=record['max_preprojection_norm_error'])
    (out/(name+'.json')).write_text(json.dumps(result,indent=2)+'\n')
    print('Completed '+name+': '+str(metric),flush=True)
    return result


def main():
    old=json.loads((ROOT/'data/processed/timestep_selection.json').read_text())
    evidence=old.get('source_hashes')
    if evidence is None:
        evidence=json.loads((ROOT/'data/processed/field_control_validation.json').read_text())['source_hashes']
    for name,expected in evidence.items():
        digest=hashlib.sha256((ROOT/name).read_bytes().replace(b'\r\n',b'\n')).hexdigest()
        if digest!=expected:
            raise ValueError('Coarser evidence uses different physics: '+name)
    with ProcessPoolExecutor(max_workers=2) as pool:
        completed=list(pool.map(run_case,['unsaturated','saturated']))
    settings=old['settings']; steps=[2,1,.5,.25]; settings['step_sizes_s']=steps
    for case,new in zip(old['cases'],completed):
        if case['config']!=new['config']:
            raise ValueError('Case parameters changed')
        case['runs']=[r for r in case['runs'] if r['step_s']!=.25]+[new['run']]
        case['comparisons']=[compare(a['metrics'],b['metrics'],settings['tolerances'])
                             for a,b in zip(case['runs'][:-1],case['runs'][1:])]
        new['output_comparisons']=[compare(a['metrics'],b['metrics'],settings['tolerances'])
                                  for a,b in zip(new['output_audit'][:-1],new['output_audit'][1:])]
    chosen=select_step(old['cases'],steps)
    output_pass=all(c['pass'] for x in completed for c in x['output_comparisons'])
    old.update(selected_step_s=chosen,status='confirmed numerical step' if chosen and output_pass else 'further refinement required')
    (ROOT/'data/processed/timestep_selection.json').write_text(json.dumps(old,indent=2)+'\n')
    final=dict(selected_step_s=chosen,output_grid_pass=output_pass,cases=completed,
               scope='Canonical geometry at gain 1e-5, with unsaturated and saturated bounds; larger engineering grids require their own audit',
               event_assumption='Piecewise linear rate norm, threshold equality qualifies; unresolved excursions cannot be proven absent',
               command='python -m studies.complete_verification')
    (ROOT/'data/processed/production_validation/confirmation.json').write_text(json.dumps(final,indent=2)+'\n')
    print('Selected step: '+str(chosen)+'; output audit pass: '+str(output_pass),flush=True)


if __name__=='__main__':
    main()
