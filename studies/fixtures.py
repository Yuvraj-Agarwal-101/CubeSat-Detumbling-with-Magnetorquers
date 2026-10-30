"""Synthetic output fixture ONLY. Not a magnetic model or an integrator."""
import numpy as np


def simulate(case, dt):
    end=case['metrics']['deadline_s']
    t=np.linspace(0,end,int(np.ceil(end/dt))+1)
    rate=np.deg2rad(case['spin_deg_s'])*np.exp(-t/1200)
    y=np.zeros((len(t),7));y[:,0]=1;y[:,4]=rate
    raw=np.zeros((len(t),3));raw[:,0]=case['dipole_limit_Am2']*(0.5+np.exp(-t/1000))
    m=raw.copy();m[:,0]=np.minimum(raw[:,0],case['dipole_limit_Am2'])
    return dict(t=t,states=y,raw_dipole=raw,dipole=m,torque=np.zeros_like(m))
