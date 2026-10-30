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
    text=r'''\subsection{Additional terminal error verification}
These six grid studies measure terminal errors with their own stated
parameters. They complement the time weighted norm studies rather than
using an interchangeable error measure.
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
\includegraphics[width=\linewidth]{convergence.png}
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
Three additional integration tests connect the shared dynamics to the common RK4 implementation using
artificial zero torque control. They check exact spherical rotation, fresh
callback evaluation at all stages, and decreasing energy and inertial momentum
errors for an asymmetric torque free trajectory. The quaternion, instantaneous dynamics, configuration
and report consistency checks are also retained. Twenty two additional checks exercise the implemented orbital field and normalized
controller against independent geometry, derivative, saturation and power identities.

\subsubsection{Production step study status}
The real idealized field and controller and the full model adapter are now implemented.
Measured full model refinement and the accepted baseline step are tabulated in the following
subsections. No ensemble engineering sweep is claimed. The supplied driver requires
both regimes and compares two successive refinements before accepting a
candidate. The predeclared tolerances are one percent relative change in detumbling
time, final rate, and peak torque, with absolute floors of $1\ \mathrm{s}$,
$10^{-6}\ \mathrm{rad/s}$, and $10^{-10}\ \mathrm{N\,m}$ respectively.
Saturation fraction uses an absolute tolerance of $0.005$. Success
classification must remain unchanged. The baseline numerical acceptance uses these declared tolerances. Broader engineering settings require their own audit. Near zero, the absolute floors control the comparison.

Every full model case must run for six orbital periods. A successful case
requires the entire $600\ \mathrm{s}$ hold interval at or below $0.5$ degrees per
second to end by the deadline. Missing times remain absent. The screening
driver uses stored endpoints for the first qualifying sampled hold interval,
peak torque, and trapezoidal time weighting of the saturation indicator.
It can miss excursions or peaks between samples. Saturation crossings can
reduce smooth convergence order and event sampling can dominate metric
differences. The separate output audit below holds the finest trajectory fixed to assess event sampling independently of integration error. Additional engineering settings require their own event resolution checks. A missed deadline says
nothing conclusive about eventual recovery.
'''
    out=ROOT/'report/sections/person2_verification.tex'
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(text,encoding='utf-8')
    copyable='# Copyable LaTeX report contributions\n\nRequired packages are amsmath and graphicx. Compile the preview from the report directory. The standalone and shared sources are compiled during final validation; see the completion record. Required bibliography entries are in report/references.bib.\n'
    for section in ('method','verification','numerical_verification','person2_verification','lecture_alignment','physics_verification','full_model_verification','production_step','acknowledgments'):
        content=(ROOT/'report/sections'/f'{section}.tex').read_text(encoding='utf-8')
        copyable+='\n## '+section+'\n\n```latex\n'+content+'```\n'
    (ROOT/'report/PERSON2_FRAGMENTS.md').write_text(copyable,encoding='utf-8')


if __name__=='__main__': run()
