# Numerical design

## Model and approximation

The physical model gives seven ordinary differential equations and all initial state components at one instant. The stored state is a real vector. Its four attitude components satisfy an additional unit constraint. That constrained set is not a vector subspace, so component updates and orientation normalization are documented separately.

The physics functions do not choose a time step or advance the solution. Case inputs contain parameters and provenance. Numerical functions accept any compatible derivative. Study drivers choose exact problems, run refinements, measure errors, and generate evidence.

## Linear algebra

Quaternion multiplication uses scalar products and cross products. Rotation matrices transform vector components between documented bases. The inertia defines a positive quadratic energy. Shared validation checks symmetry and positive eigenvalues. Euler acceleration is a linear system solved with np.linalg.solve rather than by forming a matrix inverse. The same validation is used by the model and input loader.

## Time methods

The identity relating a step to the integral of its derivative motivates forward Euler, Heun, and classical RK4. The implementations expose their stages directly. There is no external time integration library. Numerical callbacks use f(u, t), while the public physical rhs(t, u, config) is retained through an explicit adapter.

A known predicted end state can be evaluated in an explicit method. The distinction between explicit and implicit concerns unknown state dependence, not the presence of the end time in a function call.

Every internal stage is evaluated at its own time and predicted state. Projection is applied once after a completed step. Its correction norm is recorded, and exact quaternion rotation tests verify the projected algorithm separately. The last step is shortened to reach the requested final time instead of rounding the duration to an unrelated grid.

## Error and fitting

Exact state and approximate state use distinct notation. The residual of an exact one step update divided by dt is the normalized truncation error. It has order four for RK4. The corresponding single step state defect has order five. Stable accumulation on a fixed smooth interval gives fourth order global error.

Trajectory norms include trapezoidal time weights. A changing number of samples therefore does not alter the norm just by changing vector length. Quaternion errors account for equivalent signs. Rate and attitude errors are not mixed into an unscaled norm.

Convergence order is fitted in a constant and centered linear basis for logarithmic data. Those columns are orthogonal under the discrete sample inner product. The slope is a projection ratio. This avoids an unnecessary high degree monomial fit.

## Stability and stiffness

The amplification polynomial is obtained by applying each explicit method to scalar exponential evolution. It is checked against implemented steps. A decaying mode needs amplification magnitude below one. Stability alone is not accuracy.

The local Jacobian is estimated with centered differences when the derivative is smooth. Eigenvalues identify decay, physical growth, oscillation, and zero modes. A ratio is formed only among nonzero eigenvalues. A ratio by itself does not establish stiffness, and frozen eigenvalues do not prove stability of a nonlinear time varying problem or rule out transient amplification.

The production saturated magnetic trajectory needs its own accuracy and stability assessment. Saturation boundaries can change smoothness. No universal fourth order, nonstiffness, recovery guarantee, or production step is inferred from the exact verification cases.

## Approximation scope

The baseline has no spatial differential equation. It therefore needs neither a spatial boundary condition assembly nor a global or local weak form discretization. Its recovery is not a periodic function over the study interval. The numerical design uses the approximation that fits the actual initial value problem rather than adding unrelated spatial or periodic machinery.

## Evidence

The tests include exact linear, nonlinear, time dependent, complex oscillatory, and spherical rotation problems. Saved studies compare first, second, and fourth order methods, check torque free invariants over finite trajectories, and evaluate linear amplification independently of convergence.

The baseline magnetic model is still incomplete. Exact verification figures are evidence about numerical approximation and the stated rigid body special cases, not evidence of engineering detumbling performance.
