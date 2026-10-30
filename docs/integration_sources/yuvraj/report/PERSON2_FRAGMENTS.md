# Copyable LaTeX report contributions

Required packages are amsmath and graphicx. Compile the shared report main document.

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

The production magnetic model has not yet been assembled, so it has not been established that its complete dynamics are nonstiff. A production step must satisfy both accuracy requirements and the relevant stability restrictions. If stability forces steps far below those needed for accuracy, an implicit method should be assessed rather than claiming that high order alone resolves stiffness.

\subsection{Nonsmooth control and method scope}
Vector norm saturation produces a continuous command with a possible derivative change at its boundary. Fourth order results for a smooth test do not guarantee fourth order across such transitions. The saturated model requires its own step refinement study using detumbling time, success classification, and other engineering outputs.

This is a finite dimensional initial value problem with all state data specified at the initial time. No spatial differential equation or conditions at separate spatial boundaries are part of the baseline. Time marching therefore supplies the required approximation. Polynomial fits across the entire attitude history, periodic interpolation of a nonperiodic recovery, and spatial weak form discretizations are unnecessary for this model.
```

## verification

```latex
\section{Correct implementation and verification}
\input{sections/quaternion_verification}
\input{sections/dynamics_verification}
\input{sections/configuration_verification}

\input{sections/numerical_verification}
\input{sections/person2_verification}
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
errors for an asymmetric torque free trajectory. The quaternion, instantaneous dynamics, configuration,
numerical algorithm and report consistency checks are also retained. These checks do not
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
requires the entire $600\ \mathrm{s}$ hold interval at or below $0.5$ degrees per
second to end by the deadline. Missing times remain absent. The screening
driver uses stored endpoints for the first qualifying sampled hold interval,
peak torque, and trapezoidal time weighting of the saturation indicator.
It can miss excursions or peaks between samples. Saturation crossings can
reduce smooth convergence order and event sampling can dominate metric
differences. Person 4 must review event resolution separately from trajectory
error, with additional refinement where necessary. A missed deadline says
nothing conclusive about eventual recovery.
```

## acknowledgments

```latex
\section{Acknowledgments}
Generative AI assisted with project ideation, model specification, handoff preparation, repository setup, physics and configuration implementation, numerical methods, verification studies, test design, interface documentation, and LaTeX drafting. Automated tests and exact solution studies were executed during development. AI assisted checks do not establish independent human review. The generated figures show numerical verification, not magnetic detumbling performance. The team must update this account to describe actual use during the remaining control, engineering experiments, and report work.
```
