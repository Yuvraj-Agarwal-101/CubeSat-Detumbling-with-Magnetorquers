# Copyable LaTeX report contributions

Required packages are amsmath and graphicx. Compile the preview from the report directory. LaTeX compilation remains unverified.

## method

```latex
\section{Numerical method}
We advance $\dot y=f(t,y)$ with classical explicit RK4. For a step
$h_n=\min(h,T-t_n)$ the update is
\begin{align}
k_1&=f(t_n,y_n), & k_2&=f(t_n+h_n/2,y_n+h_nk_1/2),\\
k_3&=f(t_n+h_n/2,y_n+h_nk_2/2), & k_4&=f(t_n+h_n,y_n+h_nk_3),\\
\widetilde y_{n+1}&=y_n+\frac{h_n}{6}(k_1+2k_2+2k_3+k_4).
\end{align}
Each stage evaluates the derivative at its own time and state, including
forcing and control when the complete model is connected. Four derivative
evaluations are used per step. The last step ends at the specified final time.

To derive the order, augment the nonautonomous system by $\dot t=1$ and
match the elementary differentials in its Taylor expansion. The coefficients are
\[
A=\begin{pmatrix}0&0&0&0\\1/2&0&0&0\\0&1/2&0&0\\0&0&1&0\end{pmatrix},
\quad b=\begin{pmatrix}1/6\\1/3\\1/3\\1/6\end{pmatrix},
\quad c=A\mathbf1=\begin{pmatrix}0\\1/2\\1/2\\1\end{pmatrix}.
\]
Writing powers of $c$ componentwise and $C=\operatorname{diag}(c)$,
the Taylor matching conditions through order four are
\begin{align}
b^T\mathbf1&=1,&b^Tc&=1/2,&b^Tc^2&=1/3,&b^TAc&=1/6,\\
b^Tc^3&=1/4,&b^TCAc&=1/8,&b^TAc^2&=1/12,&b^TA^2c&=1/24.
\end{align}
Direct substitution satisfies all eight conditions. With sufficiently bounded
derivatives through order five and a Lipschitz right hand side in a neighborhood
of the solution, the one step defect from exact initial data is $O(h_n^5)$.
Lecture 11 divides this defect by the step length when defining truncation
error. With $\Phi_h$ denoting one unprojected RK4 update, its convention gives
\[
\tau_n=\frac{y(t_n+h_n)-\Phi_{h_n}(t_n,y(t_n))}{h_n}=O(h_n^4).
\]
Thus fifth order one step defect and fourth order truncation error per unit
time describe the same method. The Adams moment conditions in Lecture 11
do not apply directly to RK stage states. The eight conditions above account
for the intermediate states and time dependence.
The error recurrence has the form
\[
\|e_{n+1}\|\leq(1+L_*h_n)\|e_n\|+K h_n^5.
\]
Over a fixed finite interval, summing the propagated defects yields global error
$O(h^4)$. These smoothness assumptions need separate consideration at saturation
crossings. Agreement between refined numerical trajectories alone is not a
verification of the governing equations.

For $\dot y=\lambda y$, substitution of the four stages gives
\[
y_{n+1}=R(z)y_n,\qquad
R(z)=1+z+z^2/2+z^3/6+z^4/24,\qquad z=h\lambda.
\]
Following Lecture 12, strict modal decay requires $|R(z)|<1$.
Equality is the marginal boundary, not strict decay. On the imaginary axis,
$|R(i\xi)|^2=1-\xi^6/72+\xi^8/576$, so the stable interval is
$|\xi|\leq2\sqrt2$. This linear result does not establish nonlinear accuracy.
On the negative real axis the bounded region extends to approximately
$z=-2.785$. Consequently a fast decaying mode can restrict an explicit step
even when its amplitude is small. Lecture 13 distinguishes that stability
restriction from the step needed to resolve the desired dynamics.
Frozen Jacobian spectra should be reviewed at representative trajectory
states and across gains. Neutral modes must be counted separately when
forming a ratio of nonzero mode magnitudes. Nonnormality, time dependence,
projection and saturation prevent this check from being a full nonlinear
stability proof. No full model stiffness classification has been measured.
For a frozen field, the unsaturated rotational part of the normalized feedback
has torque $-k_B(I-bb^T)\omega$, where $b=B_B/\|B_B\|$.
The preliminary gain and inertia give a largest damping scale
$k_B/J_{\min}=1.43\times10^{-3}\ \mathrm{s}^{-1}$.
At the preliminary rate of $10$ degrees per second, the quaternion frequency
is $\|\omega\|/2=0.0873\ \mathrm{s}^{-1}$.
These are scale estimates, not a stiffness classification or an accepted step.
Orbital forcing, rigid body coupling, gain sweeps, and saturation still require
the complete model assessment.

After each completed step we record $\|\widetilde q_{n+1}\|-1$, then set
$q_{n+1}=\widetilde q_{n+1}/\|\widetilde q_{n+1}\|$ while leaving angular
velocity unchanged. The input quaternion must already have unit norm.
Projection is smooth near a unit quaternion and fixes the exact solution,
so it preserves fourth order there. Intermediate stages are not projected by
the integrator. The verification fixture uses polynomial quaternion kinematics
and evaluates no attitude matrix in its derivative. The shared dynamics module uses a normalized local copy for rotation matrix
evaluation and retains the unprojected stage value in quaternion kinematics.
The new integration checks exercise that contract with artificial zero torque
control. Production magnetic field and control verification remains pending.

\begin{enumerate}
\item Evaluate the four derivatives using the stage times and states.
\item Form the weighted update and record the norm error before projection.
\item Project only the completed quaternion and store the state and time.
\item Repeat until the deadline, shortening the final step when needed.
\end{enumerate}
RK4 offers fourth order accuracy for smooth trajectories with four evaluations
per step and no nonlinear solve. It is a candidate for this model because the
right hand side is small and explicit. Its production accuracy and cost remain
subject to measured full model refinement. The present implementation stores
all accepted states, using memory proportional to the number of steps.
```

## verification

```latex
\section{Correct implementation and verification}
\input{sections/quaternion_verification}
\input{sections/dynamics_verification}
\input{sections/configuration_verification}
\input{sections/numerical_verification}
\input{sections/lecture_alignment}
\input{sections/physics_verification}
\input{sections/full_model_verification}
```

## numerical_verification

```latex
\subsection{Numerical integration verification}
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
0.2 & $8.312557\times10^{-4}$ & {} & 1 & $1.759905\times10^{-3}$ & {} \\
0.1 & $5.856511\times10^{-5}$ & 3.8272 & 0.5 & $1.138071\times10^{-4}$ & 3.9508 \\
0.05 & $3.879138\times10^{-6}$ & 3.9162 & 0.25 & $7.173002\times10^{-6}$ & 3.9879 \\
0.025 & $2.494540\times10^{-7}$ & 3.9589 & 0.125 & $4.492528\times10^{-7}$ & 3.9970 \\
0.0125 & $1.581231\times10^{-8}$ & 3.9797 & 0.0625 & $2.809300\times10^{-8}$ & 3.9992 \\
0.00625 & $9.952306\times10^{-10}$ & 3.9899 & 0.03125 & $1.756042\times10^{-9}$ & 3.9998 \\
\hline
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
The finest observed orders were 3.9899 for the scalar problem and 3.9998 for rotation.
At the finest rotational step the quaternion component error was $8.780208\times10^{-10}$ and the maximum absolute norm error before projection was $1.276756\times10^{-14}$.
Angular velocity error was exactly zero in the stored double precision
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
and report consistency checks are also retained. Twenty two additional checks exercise the implemented orbital field and normalized
controller against independent geometry, derivative, saturation and power identities.

\subsubsection{Production step study status}
The real idealized field and controller and the full model adapter are now implemented.
Measured full model refinement, when available, is tabulated in the following
subsection. No ensemble engineering sweep is claimed. The supplied driver requires
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
```

## lecture_alignment

```latex
\subsection{Lecture alignment checks}
Lecture 11 defines truncation error as the one step defect divided by $h$.
For $u'=u$, $u(0)=1$, each row below starts from the exact initial state.
The numerical update is unprojected RK4 and the reference is the exponential.
\begin{center}
\begin{tabular}{rrrr}
$h$ & Defect & Defect divided by $h$ & Defect order \\
\hline
0.4 & 9.1364e-05 & 2.2841e-04 & {} \\
0.2 & 2.7582e-06 & 1.3791e-05 & 5.0499 \\
0.1 & 8.4742e-08 & 8.4742e-07 & 5.0245 \\
0.05 & 2.6260e-09 & 5.2520e-08 & 5.0121 \\
0.025 & 8.1721e-11 & 3.2688e-09 & 5.0060 \\
\end{tabular}
\end{center}
The fifth order defect yields fourth order truncation error per unit time.
At very small steps floating point cancellation would limit this comparison.

Lectures 12 and 13 use the frozen Jacobian
$A=\left(\begin{smallmatrix}-2&0\\400&-2000\end{smallmatrix}\right)$.
Its eigenvalues are $-2$ and $-2000$, with magnitude ratio $1000$.
For $h=0.001$ the fast scaled eigenvalue is $-2$, inside the RK4 region.
For $h=0.0015$ it is $-3$, outside. This constant coefficient verification
fixture demonstrates the stability restriction. It does not classify the
full CubeSat system as stiff or nonstiff.

Following Lecture 3 and the grid norm discussion in Lecture 14, convergence
records additionally store the time weighted norm
$\sqrt{\int_0^T e(t)^2\,dt}$ using trapezoidal quadrature, and the largest
sampled error. Scalar error and attitude angle error in radians are separate.
No norm mixes quaternion components and dimensional angular rates.
Time weighting includes the shortened final interval and prevents sample
count from changing the meaning of a trajectory norm. Endpoint error remains
the primary convergence plot. Sampled norms are not continuous error bounds.
```

## physics_verification

```latex
\subsection{Orbital field and control verification}
The circular orbit and tilted rotating dipole use the canonical assumed
parameters. The analytic total field derivative includes both orbital motion
and Earth rotation. Dynamics applies the body rotation correction once.
Independent centered differences give the derivative errors below.
\begin{center}
\begin{tabular}{rrr}
Time & Difference interval & Derivative error norm \\
\hline
0 & 2 & 2.14779e-13 \\
0 & 1 & 5.36947e-14 \\
0 & 0.5 & 1.34237e-14 \\
123 & 2 & 2.14986e-13 \\
123 & 1 & 5.37465e-14 \\
123 & 0.5 & 1.34366e-14 \\
3456 & 2 & 2.20238e-13 \\
3456 & 1 & 5.50595e-14 \\
3456 & 0.5 & 1.37649e-14 \\
\end{tabular}
\end{center}
Time and interval are in seconds and error is in tesla per second. The
centered difference errors decrease under refinement, independently of the
RK4 time update. Tests also verify orbit radius, period and orientation,
the polar to equatorial field strength ratio of two, zero commands, clipping
boundaries, vector rather than component saturation, torque orthogonality,
repeatability and consistent assembly in the full dynamics.

For a static inertial field and unit body field direction $b$, the
unsaturated torque is $-k_B(I-bb^T)\omega$. Thus power is
$-k_B\|\omega-(b^T\omega)b\|^2$. Saturation scales this by a factor in
$(0,1]$. Independent tests verify both regimes. This check does not imply
monotonic kinetic energy under a changing orbital field. The model remains
an idealized assumed field, not an epoch specific measured prediction.
```

## full_model_verification

```latex
\subsection{Full model numerical refinement}
The study uses the implemented circular orbit, rotating tilted dipole,
normalized B dot control and vector norm saturation. Each case runs to six
orbital periods from the canonical initial state. The unsaturated limit is
$1\ \mathrm{A\,m^2}$ and the saturated limit is $0.01\ \mathrm{A\,m^2}$.
These are numerical verification choices, not revised baseline hardware claims.
\begin{center}
\begin{tabular}{lrrrrr}
Case & $h$ & Success & $t_d$ & Final rate & Saturation \\
\hline
unsaturated & 2 & 1 & 16138.00 & 0.002165 & 0.000000 \\
unsaturated & 1 & 1 & 16135.00 & 0.002165 & 0.000000 \\
unsaturated & 0.5 & 1 & 16135.00 & 0.002165 & 0.000000 \\
saturated & 2 & 1 & 24596.00 & 0.002638 & 0.367581 \\
saturated & 1 & 1 & 24568.00 & 0.002717 & 0.367595 \\
saturated & 0.5 & 1 & 24567.00 & 0.002719 & 0.367647 \\
\end{tabular}
\end{center}
Times and steps are in seconds, final rates in radians per second, and
saturation is a time fraction. Full precision records also include peak
torque, effort, runtime, evaluation counts and norm diagnostics.
No tested step passed all declared comparisons across both cases. Further refinement is required.
The declared relative tolerances are one percent for time, final rate
and peak torque, with absolute floors of one second, $10^{-6}$ radians per
second and $10^{-10}$ newton metres. Saturation fraction uses $0.005$ absolute.
The JSON records every comparison and classification. Screening acceptance
does not approve every gain, initial geometry or case near a success boundary.
The metrics use sampled output; threshold intervals, saturation crossings
and narrow torque peaks can be unresolved. Separate output grid refinement
and representative engineering cases remain necessary before production sweeps.
A deadline failure does not establish that eventual recovery is impossible.
```

## acknowledgments

```latex
\section{Acknowledgments}
Generative AI assisted with the engineering premise, quaternion utilities,
Euler dynamics, independent checks, and report text as recorded in the workchunk records. AI also assisted with the shared
configuration, parameter table, field conventions and report assembly. For the Person 2 contribution, OpenAI Codex extracted
the handoff, implemented RK4, developed exact solution checks and convergence
studies, generated the convergence figure, and drafted the method and
verification sections. It also integrated the contribution with the shared
repository and tested the existing dynamics with the new integrator using
explicitly artificial zero torque fixtures. At the user's request, Codex subsequently implemented the idealized orbital field,
analytic derivative, normalized control and their independent tests, and
connected them for full model numerical studies. Students must review, understand, and
independently verify the generated work. The team must update this statement
to reflect subsequent AI use and actual student responsibilities.
```
