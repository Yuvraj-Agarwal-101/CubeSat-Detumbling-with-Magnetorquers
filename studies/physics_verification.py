"""Persist independent field derivative and static power identity evidence."""
import hashlib
import json
from pathlib import Path
import numpy as np
from src.config import load_config, runtime_config
from src.orbit_field import field_model
from src.controller import controller

ROOT=Path(__file__).resolve().parents[1]


def run():
    document=load_config()
    config=runtime_config(document,field_model=field_model,controller=controller)
    records=[]
    for t in [0.,123.,3456.]:
        exact=field_model(t,config)[1]
        for h in [2.,1.,.5]:
            observed=(field_model(t+h,config)[0]-field_model(t-h,config)[0])/(2*h)
            records.append(dict(time_s=t,difference_interval_s=h,
                                absolute_error_T_s=float(np.linalg.norm(observed-exact))))
    powers=[]
    b=np.array([1e-5,2e-5,-3e-5]); omega=np.array([.1,-.2,.3])
    for limit in [1.,.001]:
        config['controller_settings']['max_dipole_a_m2']=limit
        command=controller(0,None,omega,b,-np.cross(omega,b),config)
        scale=min(1.,limit/np.linalg.norm(command['raw_dipole']))
        expected=-scale*config['controller_settings']['gain_kg_m2_s']*(omega@omega-(omega@b)**2/(b@b))
        powers.append(dict(limit_A_m2=limit,measured_power_W=float(omega@command['torque']),
                           expected_power_W=float(expected),saturated=command['saturated']))
    sources = ['src/orbit_field.py', 'src/controller.py', 'team_adapter.py',
               'src/physics/dynamics.py', 'src/physics/quaternion.py',
               'src/integrators.py', 'src/numerics/integrators.py',
               'studies/physics_verification.py']
    record=dict(configuration=document,seed=None,scope='Independent finite difference and static field identity checks, not detumbling histories',
                command='python -m studies.physics_verification',
                source_sha256={p: hashlib.sha256((ROOT/p).read_bytes().replace(b'\r\n', b'\n')).hexdigest()
                               for p in sources},
                derivative_checks=records,power_checks=powers,
                power_fixture=dict(field_T=b.tolist(),omega_rad_s=omega.tolist()))
    (ROOT/'data/processed/physics_verification.json').write_text(json.dumps(record,indent=2)+'\n')
    text=r'''\subsection{Orbital field and control verification}
The circular orbit and tilted rotating dipole use the canonical assumed
parameters. The analytic total field derivative includes both orbital motion
and Earth rotation. Dynamics applies the body rotation correction once.
Independent centered differences give the derivative errors below.
\begin{center}
\begin{tabular}{rrr}
Time & Difference interval & Derivative error norm \\
\hline
'''
    for row in records:
        text+=f"{row['time_s']:g} & {row['difference_interval_s']:g} & {row['absolute_error_T_s']:.5e} "+chr(92)*2+'\n'
    text+=r'''\end{tabular}
\end{center}
Time and interval are in seconds and error is in tesla per second. The
centered difference errors decrease under refinement, independently of the
RK4 time update. Tests also verify orbit radius, period and orientation,
the polar to equatorial field strength ratio of two, zero commands, clipping
boundaries, vector rather than component saturation, torque orthogonality,
repeatability and consistent assembly in the full dynamics.

For a static inertial field, $\dot B_B=-\omega\times B_B$, so the
unsaturated command is $m=k_B(\omega\times B_B)/\|B_B\|^2$.
The vector triple product gives
$(\omega\times B_B)\times B_B=B_B(\omega^TB_B)-\omega\|B_B\|^2$.
For unit body field direction $b$, the torque is therefore
$-k_B(I-bb^T)\omega$. With constant symmetric inertia,
$E=\tfrac12\omega^TJ\omega$ and Euler's equation give
$\dot E=\omega^T\tau=-k_B\|\omega-(b^T\omega)b\|^2$,
because $\omega^T(\omega\times J\omega)=0$.
Saturation scales this by a factor in
$(0,1]$. Independent tests verify both regimes. This check does not imply
monotonic kinetic energy under a changing orbital field. In that case an
additional unsaturated torque
$-k_B[(C_{BI}\dot B_I)\times B_B]/\|B_B\|^2$ contributes power of
unrestricted sign. The normalized gain has units $\mathrm{kg\,m^2/s}$,
so the command has units $\mathrm{A\,m^2}$ and power has units watts.
The merged-source Person 3 review also checks inverse-cube scaling,
separate orbit and field periodicity, nontrivial attitudes, and all real
adapter RK4 stages. These instantaneous and short-horizon checks do not
renew the historical one second timestep acceptance. The model remains
an idealized assumed field, not an epoch specific measured prediction.
'''
    (ROOT/'report/sections/physics_verification.tex').write_text(text)


if __name__=='__main__':
    run()
