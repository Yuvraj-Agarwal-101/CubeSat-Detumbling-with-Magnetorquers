"""Person 4 audit of real adapter outputs at h, h/2, h/4.

This runs preliminary diagnostic simulations before production approval.
It supplies evidence for Person 2, never approves its own time step.
"""
import argparse
import importlib
import json
from pathlib import Path
import time
import numpy as np
from src.experiments import generate_cases
from src.metrics import compute_metrics
from src.numerical_diagnostics import common_samples,scaled_state_error,metric_changes,modal_diagnostics


def load_function(spec):
    module,name=spec.split(':');return getattr(importlib.import_module(module),name)


def audit(case,simulate,step,rhs=None):
    if not np.isfinite(step) or step<=0: raise ValueError('positive finite step required')
    runs=[];metric=[];cost=[]
    for h in (step,step/2,step/4):
        start=time.perf_counter();result=simulate(case,h);cost.append(time.perf_counter()-start)
        metric.append(compute_metrics(**{k:result[k] for k in
            ('t','states','raw_dipole','dipole','torque')},settings=case['metrics'],limit=case['dipole_limit_Am2']))
        runs.append(result)
    comparison=[]
    for i in (0,1):
        a,b=runs[i:i+2]
        reference=common_samples(a['t'],b['t'],b['states'])
        comparison.append(scaled_state_error(a['t'],a['states'],reference,
                          rate_scale=case['metrics']['threshold_rad_s']))
    e=[x['scaled_time_rms'] for x in comparison]
    result=dict(case=case,steps_s=[step,step/2,step/4],runtime_s=cost,metrics=metric,
                state_differences=comparison,metric_changes=[metric_changes(a,b) for a,b in zip(metric[:-1],metric[1:])],
                observed_difference_order=None if min(e)==0 else float(np.log2(e[0]/e[1])),
                approved=False,scope='Preliminary numerical diagnostic; not a production approval',
                limitations='Self convergence does not verify the equations. Saturation and threshold functionals can reduce observed order. Compare against independent physics checks.')
    # Hold the finest integrated trajectory fixed and coarsen only its output.
    output_metrics=[]
    fine=runs[-1]
    for stride in (4,2,1):
        nodes=np.unique(np.r_[np.arange(0,len(fine['t']),stride),len(fine['t'])-1])
        output_metrics.append(compute_metrics(**{k:np.asarray(fine[k])[nodes] for k in
            ('t','states','raw_dipole','dipole','torque')},settings=case['metrics'],limit=case['dipole_limit_Am2']))
    result['output_only_metric_changes']=[metric_changes(a,b) for a,b in zip(output_metrics[:-1],output_metrics[1:])]
    result['output_only_metrics']=output_metrics
    if rhs is not None:
        modes=[];fine=runs[-1]
        for idx in np.unique(np.linspace(0,len(fine['t'])-1,5,dtype=int)):
            t=float(fine['t'][idx]);y=np.asarray(fine['states'][idx],float)
            scale=np.r_[np.ones(4),np.full(3,case['metrics']['threshold_rad_s'])]
            # Scaled central differences. Repeat with different perturbations in a full audit.
            eps=np.cbrt(np.finfo(float).eps);jac=np.empty((7,7))
            for j in range(7):
                delta=np.zeros(7);delta[j]=eps*max(abs(y[j]),scale[j])
                jac[:,j]=(rhs(t,y+delta,case)-rhs(t,y-delta,case))/(2*delta[j])
            modes.append(dict(time_s=t,**modal_diagnostics(jac,step)))
        result['frozen_modal_diagnostics']=modes
    return result,runs


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--adapter',required=True)
    p.add_argument('--rhs-adapter',help='optional module:function with rhs(t,y,case)')
    p.add_argument('--config',default='configs/study.json');p.add_argument('--case-index',type=int,default=0)
    p.add_argument('--step',required=True,type=float);p.add_argument('--output',required=True)
    a=p.parse_args();cases=list(generate_cases(json.loads(Path(a.config).read_text(encoding='utf-8'))))
    if not 0<=a.case_index<len(cases):p.error('case-index outside pilot')
    out=Path(a.output);out.mkdir(parents=True,exist_ok=False)
    result,histories=audit(cases[a.case_index],load_function(a.adapter),a.step,
                          None if not a.rhs_adapter else load_function(a.rhs_adapter))
    for i,history in enumerate(histories):np.savez_compressed(out/f'level_{i}.npz',**history)
    (out/'audit.json').write_text(json.dumps(result,indent=2,allow_nan=False),encoding='utf-8')
