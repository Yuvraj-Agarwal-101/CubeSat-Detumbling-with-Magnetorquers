# Copyable LaTeX report contributions

Required packages are amsmath and graphicx. Compile the preview from the report directory. The standalone and shared sources are compiled during final validation; see the completion record. Required bibliography entries are in report/references.bib.

## method

```latex
\section{Numerical method}

\subsection{Time marching from the initial value problem}
Write the state equation as
\[
\dot u=f(u,t),\qquad u(t_0)=u_0,\qquad
t_k=t_0+k\Delta t.
\]
The symbol \(u(t_k)\) denotes the exact state and \(u_k\) its computed approximation. The model retains the public call \texttt{rhs(t, u, config)}. A state first numerical callback is formed by evaluating that function with the arguments in the required order.

Integrating the differential equation across one step gives
\[
u(t_{k+1})=u(t_k)+\int_{t_k}^{t_{k+1}}f(u(t),t)\,dt.
\]
The numerical method approximates this integral using slopes evaluated at known or predicted states. Forward Euler uses one slope. Heun uses an Euler prediction and averages two slopes. Classical RK4 uses four stages and is the primary method for the smooth verification problems.

\subsection{Classical RK4}
For a step of length \(h=\Delta t\), define
\begin{align*}
y_1&=f(u_k,t_k),\\
y_2&=f(u_k+\tfrac12hy_1,t_k+\tfrac12h),\\
y_3&=f(u_k+\tfrac12hy_2,t_k+\tfrac12h),\\
y_4&=f(u_k+hy_3,t_k+h).
\end{align*}
The update is
\[
u_{k+1}=u_k+\frac{h}{6}(y_1+2y_2+2y_3+y_4).
\]
Every argument is available before its slope is evaluated, so the method is explicit. An evaluation at the end time does not make the method implicit when its state is a known prediction. Four derivative evaluations are needed per step.

To verify the order for a general smooth problem, include time as an additional component, so the equation is autonomous. Let \(A\) contain the stage coefficients, \(b\) the weights, \(c=A{\bf1}\), and \(C=\operatorname{diag}(c)\). Here
\[
A=\begin{pmatrix}
0&0&0&0\\
1/2&0&0&0\\
0&1/2&0&0\\
0&0&1&0
\end{pmatrix},
\quad
b=\begin{pmatrix}1/6\\1/3\\1/3\\1/6\end{pmatrix},
\quad
c=\begin{pmatrix}0\\1/2\\1/2\\1\end{pmatrix}.
\]
Expanding the stages in Taylor series and matching the exact solution through degree four requires
\[
\begin{aligned}
b^T{\bf1}&=1,&b^Tc&=1/2,\\
b^Tc^2&=1/3,&b^TAc&=1/6,\\
b^Tc^3&=1/4,&b^TCAc&=1/8,\\
b^TAc^2&=1/12,&b^TA^2c&=1/24.
\end{aligned}
\]
Powers of \(c\) are componentwise. Substitution of the displayed coefficients satisfies all eight conditions. This checks the dependence on the predicted states as well as the integration weights.

\subsection{Truncation error and accumulated error}
Let \(\Phi_h(u,t)\) denote one complete unprojected RK4 step. Define truncation error with division by the step length
\[
\tau_k=\frac{u(t_{k+1})-\Phi_h(u(t_k),t_k)}{h}.
\]
For a sufficiently smooth right hand side, \(\tau_k=O(h^4)\). The corresponding error in a single step starting from the exact state is \(h\tau_k=O(h^5)\). These are different conventions for the local error, not different orders of the method.

The global error is \(e_k=u(t_k)-u_k\). It includes the local defect and the propagation of previous errors. For a smooth problem with bounded derivatives and stable propagation on a fixed time interval, the accumulated error is \(O(h^4)\). Measured convergence is therefore checked separately from individual algebraic identities.

The integrator uses the requested step for interior intervals and shortens the last interval to reach the final time exactly. It never changes a stage by quaternion projection. A separate callback normalizes the quaternion after a completed step. The size of this correction is recorded. The projected attitude calculation is verified independently against exact rotation.

\subsection{Absolute stability and stiffness}
For the scalar model \(\dot u=\lambda u\), substituting the four stages gives
\[
u_{k+1}=R(w)u_k,\qquad
w=h\lambda,\qquad
R(w)=1+w+\tfrac12w^2+\tfrac16w^3+\tfrac1{24}w^4.
\]
A decaying mode is represented as decaying when \(|R(w)|<1\). RK4 has a bounded stability region. Increasing order does not remove a step restriction imposed by a rapidly decaying mode. Neutral and physically growing modes must be interpreted separately.

A nonlinear assessment uses a local Jacobian \(D_uf\) at representative states, its eigenvalues, and the corresponding amplification factors. A large separation between nonzero eigenvalue magnitudes can indicate different time scales. Zero modes must be identified before forming a ratio. Eigenvalues of a frozen local Jacobian do not prove stability of a nonlinear time varying system, and nonorthogonal eigenvectors can permit transient amplification.

The idealized production magnetic model is implemented. Its complete nonlinear dynamics have not been established to be nonstiff across engineering cases. A production step must satisfy both accuracy requirements and the relevant stability restrictions. If stability forces steps far below those needed for accuracy, an implicit method should be assessed rather than claiming that high order alone resolves stiffness.

\subsection{Nonsmooth control and method scope}
Vector norm saturation produces a continuous command with a possible derivative change at its boundary. Fourth order results for a smooth test do not guarantee fourth order across such transitions. The saturated model requires its own step refinement study using detumbling time, success classification, and other engineering outputs.

This is a finite dimensional initial value problem with all state data specified at the initial time. No spatial differential equation or conditions at separate spatial boundaries are part of the baseline. Time marching therefore supplies the required approximation. Polynomial fits across the entire attitude history, periodic interpolation of a nonperiodic recovery, and spatial weak form discretizations are unnecessary for this model.

\subsection{Lecture stability interpretation and model scales}
Following Lecture 12 \cite{goza12}, strict modal decay requires $|R(z)|<1$.
Equality is the marginal boundary, not strict decay. On the imaginary axis,
$|R(i\xi)|^2=1-\xi^6/72+\xi^8/576$, so the stable interval is
$|\xi|\leq2\sqrt2$. This linear result does not establish nonlinear accuracy.
On the negative real axis the bounded region extends to approximately
$z=-2.785$. Consequently a fast decaying mode can restrict an explicit step
even when its amplitude is small. Lecture 13 \cite{goza13} distinguishes that stability
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

```

## verification

```latex
\section{Correct implementation and verification}
\input{sections/quaternion_verification}
\input{sections/dynamics_verification}
\input{sections/configuration_verification}

\input{sections/numerical_verification}
\input{sections/person2_verification}
\input{sections/lecture_alignment}
\input{sections/physics_verification}
\input{sections/full_model_verification}
\input{sections/production_step}
```

## numerical_verification

```latex
\subsection{Time integration convergence}
The scalar test is \(\dot u=-u\), \(u(0)=1\), with exact solution \(u(t)=e^{-t}\) on \(0\leq t\leq2\). Five steps from \(0.2\) through \(0.0125\) are used. The error at each sample is the exact value minus the computed value. It is measured using
\[
\|e\|_{\Delta t}
=\left(\sum_k\frac{t_{k+1}-t_k}{2}
\left(\|e_k\|_2^2+\|e_{k+1}\|_2^2\right)\right)^{1/2}.
\]
The time weights approximate an integral norm and prevent the measurement from growing merely because refinement adds samples.

A separate spherical body test sets \(J=2I_3\) and torque to zero. With constant body rate \(\omega_0\), the exact quaternion is
\[
q(t)=q(0)\otimes
\left(\cos(\|\omega_0\|t/2),
\frac{\omega_0}{\|\omega_0\|}\sin(\|\omega_0\|t/2)\right).
\]
The zero rate case is handled separately. The study uses \(\omega_0=(0.3,-0.2,0.4)^T\ \mathrm{rad/s}\), a nonidentity initial quaternion, \(t_f=4\ \mathrm{s}\), and five steps from \(0.4\) through \(0.025\ \mathrm{s}\). The attitude error is
\[
d_q=\min\bigl(\|q_{\rm exact}-q_k\|_2,\|q_{\rm exact}+q_k\|_2\bigr).
\]
This accounts for the two quaternion signs representing one orientation. Angular velocity and quaternion errors are not combined into an unscaled mixed unit norm.

Orders are estimated by fitting \(\log\|e\|_{\Delta t}=a+p\log h\). Centering \(\log h\) makes the constant and linear basis columns orthogonal under the sample inner product, so \(p\) is obtained by a projection ratio rather than a poorly conditioned polynomial fit.
\begin{table}[htbp]
\centering
\input{sections/verification_orders}
\caption{Measured orders from the saved five grid studies. Finite step effects account for small departures from the asymptotic integer orders.}
\end{table}
\begin{figure}[htbp]
\centering
\includegraphics[width=0.82\linewidth]{verification_convergence.png}
\caption{Exact scalar decay convergence. Euler, Heun, and RK4 approach first, second, and fourth order respectively. The vertical axis uses the time weighted error norm.}
\end{figure}

\subsection{Conservation over finite trajectories}
The asymmetric torque free study uses \(J=\operatorname{diag}(0.030,0.035,0.007)\ \mathrm{kg\,m^2}\), initial rate \((0.4,0.3,0.5)^T\ \mathrm{rad/s}\), and a duration of \(20\ \mathrm{s}\). Energy and the full inertial momentum vector are compared with their initial values. These are independent physical invariants rather than a finer numerical trajectory used as truth.
\begin{figure}[htbp]
\centering
\includegraphics[width=0.82\linewidth]{verification_invariants.png}
\caption{Maximum relative energy and inertial momentum errors for the asymmetric torque free body. Both decrease under refinement. Their measured powers need not coincide on every grid.}
\end{figure}
Quaternion correction norms are saved separately. Projection controls the unit constraint but does not by itself establish correct rotational dynamics.

\subsection{Linear stability checks}
For \(\lambda=-1\), the implemented RK4 step agrees with its analytic amplification polynomial. In particular, \(R(-2)=1/3\) gives decay, whereas \(R(-3)=1.375\) gives numerical growth for the same decaying differential equation. This checks stability separately from convergence order.
\begin{figure}[htbp]
\centering
\includegraphics[width=0.82\linewidth]{verification_stability.png}
\caption{Amplification magnitude on the negative real axis. The horizontal line is one. Values below it represent decay for the scalar linear model. A stable factor alone does not establish accuracy.}
\end{figure}

\subsection{Production verification still required}
These are exact solution and conservation studies for stated special cases. Production field and controller checks, saturation transition refinement, local spectral assessment along magnetic trajectories, and a production time step remain required. No detumbling time or engineering success fraction is inferred from the special cases.
```

## person2_verification

```latex
\subsection{Additional terminal error verification}
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
\includegraphics[width=\linewidth]{convergence.png}
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

Following Lecture 3 \cite{goza3} and the grid norm discussion in Lecture 14, convergence
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
unsaturated & 0.25 & 1 & 16135.00 & 0.002165 & 0.000000 \\
saturated & 2 & 1 & 24596.00 & 0.002638 & 0.367581 \\
saturated & 1 & 1 & 24568.00 & 0.002717 & 0.367595 \\
saturated & 0.5 & 1 & 24567.00 & 0.002719 & 0.367647 \\
saturated & 0.25 & 1 & 24566.75 & 0.002719 & 0.367606 \\
\end{tabular}
\end{center}
Times and steps are in seconds, final rates in radians per second, and
saturation is a time fraction. Full precision records also include peak
torque, effort, runtime, evaluation counts and norm diagnostics.
The screening gate selects $1$ seconds for these two cases after two successive refinements.
The declared relative tolerances are one percent for time, final rate
and peak torque, with absolute floors of one second, $10^{-6}$ radians per
second and $10^{-10}$ newton metres. Saturation fraction uses $0.005$ absolute.
The JSON records every comparison and classification. Screening acceptance
does not approve every gain, initial geometry or case near a success boundary.
The metrics use sampled output; threshold intervals, saturation crossings
and narrow torque peaks can be unresolved. The independent output grid audit and accepted baseline setting are documented
in the next subsection. Broader engineering cases still require their own audit.
A deadline failure does not establish that eventual recovery is impossible.
```

## production_step

```latex
\subsection{Accepted numerical production step}
The production setting in the canonical configuration is
$1$ second.
The two successive comparisons from one to half a second and from half to
a quarter second pass every declared metric tolerance in both saturation
regimes. Success classification remains unchanged. The earlier two second
saturated failure is retained in the record rather than discarded.

To separate output sampling from integration error, each quarter second
trajectory is held fixed while output spacing is coarsened. Complete hold
intervals use piecewise linear interpolation of rate norm, and saturation
duration uses crossings of the raw dipole norm. Equality qualifies in this
diagnostic, matching the Person 4 convention; the original sampled strict
threshold metric is retained for the integrator comparisons.
\begin{center}
\begin{tabular}{lrrr}
Case & Output spacing & Interpolated start & Saturation fraction \\
\hline
unsaturated & 1 & 16134.853507 & 0.00000000 \\
unsaturated & 0.5 & 16134.853387 & 0.00000000 \\
unsaturated & 0.25 & 16134.853327 & 0.00000000 \\
saturated & 1 & 24566.691807 & 0.36759482 \\
saturated & 0.5 & 24566.691441 & 0.36759145 \\
saturated & 0.25 & 24566.691327 & 0.36759071 \\
\end{tabular}
\end{center}
All output comparisons pass the same predeclared tolerances. Interpolation
does not prove that every continuous excursion was resolved, but refinement
supports the event resolution for these trajectories. Compact scalar
histories are supplied to reproduce this audit without reintegration.

The canonical $0.1\ \mathrm{A\,m^2}$ baseline is also integrated separately
at the accepted step. Its command bound is inactive at every evaluated RK4
stage. The maximum raw magnitude is
$0.07030255$ ampere square metres across 136036 stage calls.
Its metrics agree with the unsaturated reference to floating point
roundoff. This connects the unsaturated refinement case to the actual
baseline bound. Final contribution percentages, independent teammate
reproduction and the engineering sweep remain team responsibilities.
```

## acknowledgments

```latex
\section{Acknowledgments}
Generative AI assisted with project ideation, model specification, handoff preparation, repository setup, physics and configuration implementation, numerical methods, verification studies, test design, interface documentation, and LaTeX drafting. Automated tests and exact solution studies were executed during development. AI assisted checks do not establish independent human review. The generated figures show numerical verification, not magnetic detumbling performance. The team must update this account to describe actual use during the remaining control, engineering experiments, and report work.
```
