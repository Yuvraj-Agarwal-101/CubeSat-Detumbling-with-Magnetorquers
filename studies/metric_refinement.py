"""Verify postprocessing against exact histories, WITHOUT any ODE integrator."""
import argparse
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from src.metrics import detumbling_time, saturation_fraction


def run(output):
    out=Path(output);out.mkdir(parents=True,exist_ok=False)
    rows=[]
    for n in (16,32,64,128,256,512):
        t=np.linspace(0,4,n+1);h=4/n
        rate=4*np.exp(-t);raw=2*np.exp(-t)
        td=detumbling_time(t,rate,1,1,4)
        sat=saturation_fraction(t,raw,1)
        effort=np.sum(np.diff(t)*(np.minimum(raw[:-1],1)+np.minimum(raw[1:],1))/2)
        rows.append(dict(step_s=h,detumbling_time_s=td,time_error_s=abs(td-np.log(4)),
                         saturation_fraction=sat,saturation_error=abs(sat-np.log(2)/4),
                         effort=effort,effort_error=abs(effort-(np.log(2)+1-2*np.exp(-4)))))
    evidence=dict(scope='Exact analytic sampled histories; no spacecraft physics or IVP integration',
                  exact=dict(time_s=float(np.log(4)),saturation_fraction=float(np.log(2)/4),
                             effort=float(np.log(2)+1-2*np.exp(-4))),rows=rows,
                  interpretation='Piecewise linear crossings and trapezoid effort have second order bounds on this smooth case. Crossing location within a cell causes nonmonotone error constants.')
    (out/'evidence.json').write_text(json.dumps(evidence,indent=2),encoding='utf-8')
    fig,ax=plt.subplots(figsize=(6,4))
    for key,marker in [('time_error_s','o'),('saturation_error','s'),('effort_error','^')]:
        ax.loglog([r['step_s'] for r in rows],[r[key] for r in rows],color='black',marker=marker,label=key)
    h=np.array([r['step_s'] for r in rows]);ax.loglog(h,.1*h*h,'k--',label='Slope 2 guide')
    ax.set_xlabel('Output spacing [s]');ax.set_ylabel('Absolute error in stated metric units')
    ax.set_title('Analytic metric verification only');ax.legend(fontsize=8);fig.tight_layout()
    fig.savefig(out/'metric_refinement.pdf');fig.savefig(out/'metric_refinement.png',dpi=150);plt.close(fig)
    (out/'manifest.json').write_text(json.dumps(dict(figure='metric_refinement.pdf',
        command=f'python -m studies.metric_refinement --output {out.as_posix()}',
        source='analytic functions in studies/metric_refinement.py',seed=None,
        data='evidence.json',scope=evidence['scope']),indent=2))
    return evidence


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',default='data/processed/metric_verification')
    a=p.parse_args();print(json.dumps(run(a.output),indent=2))
