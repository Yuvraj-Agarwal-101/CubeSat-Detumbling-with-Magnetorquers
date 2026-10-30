"""Lecture 3 norms, Lecture 11 refinement, Lectures 12/13 modal diagnostics.

No integration and no automatic production-step approval. Frozen Jacobian
spectra are local diagnostics, not a nonlinear stability certificate.
"""
import numpy as np


def observed_orders(steps, errors):
    steps, errors = np.asarray(steps,float), np.asarray(errors,float)
    if (steps.ndim != 1 or errors.shape != steps.shape or len(steps)<2
            or not np.isfinite(steps).all() or not np.isfinite(errors).all()
            or np.any(steps<=0) or np.any(np.diff(steps)>=0) or np.any(errors<0)):
        raise ValueError('positive decreasing steps and nonnegative finite errors required')
    return [None if a==0 or b==0 else float(np.log(a/b)/np.log(h/k))
            for h,k,a,b in zip(steps[:-1],steps[1:],errors[:-1],errors[1:])]


def scaled_state_error(t, actual, reference, rate_scale):
    """Dimensionless time RMS and sampled max; separate quaternion/rate scales.

    Quaternion chord error is sign invariant and uses locally normalized copies.
    This is an orientation proxy, not an angular error in radians. Raw norm
    drift is separately reported so normalization cannot hide a solver defect.
    """
    t=np.asarray(t,float);a=np.asarray(actual,float);b=np.asarray(reference,float)
    if (t.ndim!=1 or len(t)<2 or np.any(np.diff(t)<=0)
            or a.shape!=(len(t),7) or b.shape!=a.shape
            or not all(np.isfinite(x).all() for x in (t,a,b))
            or not np.isfinite(rate_scale) or rate_scale<=0):
        raise ValueError('invalid time/state histories or rate scale')
    na=np.linalg.norm(a[:,:4],axis=1);nb=np.linalg.norm(b[:,:4],axis=1)
    if np.any(na==0) or np.any(nb==0): raise ValueError('zero quaternion')
    qa=a[:,:4]/na[:,None];qb=b[:,:4]/nb[:,None]
    chord=np.minimum(np.linalg.norm(qa-qb,axis=1),np.linalg.norm(qa+qb,axis=1))
    rate=np.linalg.norm(a[:,4:]-b[:,4:],axis=1)/rate_scale
    squared=chord**2+rate**2
    rms=np.sqrt(np.sum(np.diff(t)*(squared[:-1]+squared[1:])/2)/(t[-1]-t[0]))
    return dict(scaled_time_rms=float(rms),scaled_sampled_max=float(np.sqrt(squared.max())),
                quaternion_chord_max=float(chord.max()),rate_error_max_rad_s=float(rate.max()*rate_scale),
                actual_quaternion_norm_defect_max=float(np.max(np.abs(na-1))),
                reference_quaternion_norm_defect_max=float(np.max(np.abs(nb-1))))


def common_samples(coarse_t, fine_t, fine_states):
    """Require nested nodes; interpolating a reference could conceal RK4 order."""
    c=np.asarray(coarse_t,float);f=np.asarray(fine_t,float);y=np.asarray(fine_states,float)
    if (c.ndim!=1 or f.ndim!=1 or len(c)<2 or len(f)<len(c)
            or not np.isfinite(c).all() or not np.isfinite(f).all()
            or np.any(np.diff(c)<=0) or np.any(np.diff(f)<=0) or y.shape!=(len(f),7)):
        raise ValueError('invalid nested histories')
    i=np.searchsorted(f,c);i=np.minimum(i,len(f)-1)
    left=np.maximum(i-1,0);i=np.where(abs(f[left]-c)<abs(f[i]-c),left,i)
    if not np.allclose(f[i],c,rtol=0,atol=1e-10):
        raise ValueError('refinement needs nested output nodes without interpolation')
    return y[i]


def metric_changes(coarse,fine):
    """Censor changes are discrete, and never treated as zero timing error."""
    keys=('final_rate_rad_s','saturation_fraction','peak_torque_Nm','dipole_effort_Am2_s')
    a,b=coarse['detumbling_time_s'],fine['detumbling_time_s']
    return dict(success_changed=coarse['success']!=fine['success'],
                detumbling_time_change_s=None if a is None or b is None else abs(a-b),
                both_censored=a is None and b is None,
                **{key+'_absolute_change':abs(coarse[key]-fine[key]) for key in keys})


def rk4_amplification(z):
    z=np.asarray(z,complex)
    return 1+z+z*z/2+z**3/6+z**4/24


def modal_diagnostics(jacobian,step,zero_tolerance=1e-10):
    a=np.asarray(jacobian,float)
    if (a.ndim!=2 or a.shape[0]!=a.shape[1] or not np.isfinite(a).all()
            or not np.isfinite(step) or step<=0 or zero_tolerance<=0):
        raise ValueError('finite square Jacobian and positive step required')
    eig=np.linalg.eigvals(a);amp=abs(rk4_amplification(step*eig))
    neutral=abs(eig)<=zero_tolerance;growth=eig.real>zero_tolerance
    decaying=eig.real < -zero_tolerance
    sizes=abs(eig[decaying])
    return dict(eigenvalues=[dict(real=float(z.real),imag=float(z.imag)) for z in eig],
                amplification_moduli=amp.tolist(),neutral_mode_count=int(neutral.sum()),
                growing_mode_count=int(growth.sum()),
                non_growing_modes_outside_rk4=int(np.sum((~growth)&(amp>1+1e-12))),
                decaying_mode_magnitude_ratio=None if len(sizes)<2 else float(sizes.max()/sizes.min()),
                interpretation='frozen linear modal diagnostic only; check nonlinear refinement and saturation switches')
