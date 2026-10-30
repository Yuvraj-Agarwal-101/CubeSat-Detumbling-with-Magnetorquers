"""Generate the numerical verification fragment only from measured records."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]


def scientific(value):
    mantissa, exponent = f'{value:.6e}'.split('e')
    return mantissa + r'\times10^{' + str(int(exponent)) + '}'


def run():
    rows=json.loads((ROOT/'data/processed/convergence.json').read_text())['results']
    scalar=[r for r in rows if r['case']=='scalar']
    spherical=[r for r in rows if r['case']=='spherical']
    text=r'''\subsection{Numerical integration verification}
The independent scalar problem is $\dot u=tu$ with $u(0)=1$.
Separation of variables gives $u(t)=\exp(t^2/2)$ and the comparison time is
$T=2\ \mathrm{s}$. This test exercises nonautonomous stage evaluations.

For spherical inertia $J=jI$ with zero torque, Euler's equation gives
$\dot\omega=0$. The quaternion equation is
$\dot q=\tfrac12 q\otimes(0,\omega_0)$.
The square of the pure quaternion $(0,\omega_0)$ is
$(-\|\omega_0\|^2,0)$, so its exponential gives the independent solution
\[
q(t)=q(0)\otimes
\left(\cos\frac{\|\omega_0\|t}{2},
\frac{\omega_0}{\|\omega_0\|}\sin\frac{\|\omega_0\|t}{2}\right).
\]
When $\omega_0=0$, $q(t)=q(0)$. The numerical derivative uses direct component
equations and the reference uses quaternion multiplication. Neither reference
uses an external integrator. The test uses $j=0.02\ \mathrm{kg\,m^2}$,
$q(0)=(0.8,0.2,-0.4,0.4)^T$,
$\omega_0=(0.3,-0.4,0.5)^T\ \mathrm{rad/s}$, and $T=20\ \mathrm{s}$.
These are verification inputs, not the engineering baseline.
The identity mapping and the specified positive quarter turn mapping
$C_{BI}e_1=-e_2$ were checked independently in a convention fixture.

We align quaternion signs before computing component error. For the relative
unit quaternion $r=q_{\mathrm{exact}}^{-1}\otimes q_{\mathrm{num}}$, the
attitude error is $2\operatorname{atan2}(\|r_v\|,|r_s|)$.
Observed order is $p=\log_2(e_h/e_{h/2})$. Each order in the table compares
that row with the preceding row for the same problem.
\begin{table}[htbp]
\centering
\begin{tabular}{rrrrrr}
\hline
Scalar $h$ & Scalar error & $p$ & Rotation $h$ & Angle error & $p$ \\
\hline
'''
    for a,b in zip(scalar,spherical):
        pa='{}' if a['order'] is None else f"{a['order']:.4f}"
        pb='{}' if b['order'] is None else f"{b['order']:.4f}"
        text+=f"{a['step_s']:g} & ${scientific(a['error'])}$ & {pa} & {b['step_s']:g} & ${scientific(b['error'])}$ & {pb} \\\\\n"
    text+=r'''\hline
\end{tabular}
\caption{Exact solution convergence. Step sizes are in seconds and attitude
errors are in radians.}
\label{tab:person2convergence}
\end{table}
\begin{figure}[htbp]
\centering
\includegraphics[width=\linewidth]{../figures/convergence.pdf}
\caption{Measured convergence with fourth order reference slopes.}
\label{fig:person2convergence}
\end{figure}
'''
    text+=f"The finest observed orders were {scalar[-1]['order']:.4f} for the scalar problem and {spherical[-1]['order']:.4f} for rotation.\n"
    text+=f"At the finest rotational step the quaternion component error was ${scientific(spherical[-1]['quaternion_component_error'])}$ and the maximum absolute norm error before projection was ${scientific(spherical[-1]['max_preprojection_norm_error'])}$.\n"
    text+=r'''Angular velocity error was exactly zero in the stored double precision
results for this constant rate fixture. It therefore does not provide a
meaningful order estimate for the angular velocity dynamics. The chosen
attitude errors still show truncation dominated behavior. Norm diagnostics
approach floating point precision at the finest step, so they must not be
extrapolated as a convergence law.

Twenty Person 2 unit tests check stage evaluation, shortened endpoints,
projection timing, input validation, exact solutions, the frame convention,
and synthetic checks of the study's sampled metrics and refinement gate.
Three additional integration tests connect the shared dynamics to RK4 using
artificial zero torque control. They check exact spherical rotation, fresh
callback evaluation at all stages, and decreasing energy and inertial momentum
errors for an asymmetric torque free trajectory. The existing 175 quaternion, instantaneous dynamics, configuration
and report consistency checks are also retained. These checks do not
validate the unavailable production magnetic field or controller.

\subsubsection{Production step study status}
The production field and controller are unavailable. Unsaturated and saturated full model
runs, production timing, and production step selection are pending. No
production step or engineering sweep is claimed. The supplied driver requires
both regimes and compares two successive refinements before accepting a
candidate. Proposed tolerances are one percent relative change in detumbling
time, final rate, and peak torque, with absolute floors of $1\ \mathrm{s}$,
$10^{-6}\ \mathrm{rad/s}$, and $10^{-10}\ \mathrm{N\,m}$ respectively.
Saturation fraction uses an absolute tolerance of $0.005$. Success
classification must remain unchanged. The team must approve these tolerances
before production runs. Near zero, the absolute floors control the comparison.

Every full model case must run for six orbital periods. A successful case
requires the entire $600\ \mathrm{s}$ hold interval below $0.5$ degrees per
second to end by the deadline. Missing times remain absent. The screening
driver uses stored endpoints for the first qualifying sampled hold interval,
peak torque, and trapezoidal time weighting of the saturation indicator.
It can miss excursions or peaks between samples. Saturation crossings can
reduce smooth convergence order and event sampling can dominate metric
differences. Person 4 must review event resolution separately from trajectory
error, with additional refinement where necessary. A missed deadline says
nothing conclusive about eventual recovery.
'''
    out=ROOT/'report/sections/numerical_verification.tex'
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(text,encoding='utf-8')
    copyable='# Copyable LaTeX report contributions\n\nRequired packages are amsmath and graphicx. Compile the preview from the report directory. LaTeX compilation remains unverified.\n'
    for section in ('method','verification','numerical_verification','acknowledgments'):
        content=(ROOT/'report/sections'/f'{section}.tex').read_text(encoding='utf-8')
        copyable+='\n## '+section+'\n\n```latex\n'+content+'```\n'
    (ROOT/'report/PERSON2_FRAGMENTS.md').write_text(copyable,encoding='utf-8')


if __name__=='__main__': run()
