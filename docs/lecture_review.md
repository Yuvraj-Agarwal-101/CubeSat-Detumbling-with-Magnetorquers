# AE 370 lecture comparison and local revisions

Reviewed the supplied HTML decks for Lectures 2 through 19. There are 19 files and 18 lecture numbers. The two Lecture 18 files have identical extracted text. Lecture 1 is not present. Source fingerprints are listed below. These notes summarize mathematical ideas and their implications for this project, rather than reproducing the slides.

## Decision

Retain classical RK4 and the quaternion and Euler dynamics equations. The four stages match Lecture 10. The current engineering problem is an initial value problem, so the spatial boundary value methods in the later lectures do not replace its time integrator. Changes were needed to the error terminology, evidence and trajectory error measurements. No production magnetic model or validated production step is supplied by the lectures.

## Lecture notes and code implications

| Lecture | Mathematical idea | Project decision |
| --- | --- | --- |
| 2 | Vector spaces, subspaces and finite dimensional approximation | The seven component state represents a first order ODE. Unit quaternions form a constraint manifold, not a linear subspace. Keep normalization as a separate completed step projection. |
| 3 | Inner products and norms specify which errors matter; L2 requires quadrature | Add time weighted L2 and sampled maximum error to convergence records. Keep scalar and attitude error separate. Do not combine unitless quaternion entries and rad/s in one unscaled norm. |
| 4 | A basis and interpolation conditions yield Ac=b | Useful background for deriving local formulas; no global polynomial fit is needed for attitude time advancement. |
| 5 | Node distribution and basis conditioning affect interpolation and roundoff differently | Retain explicit stage formulas and stable atan2 attitude errors. Do not claim refinement can defeat roundoff or fit a high degree monomial history. |
| 6 | Cubic splines enforce interpolation and derivative continuity, with boundary conditions | Spline fitting would introduce new assumptions at saturation or hold threshold crossings. Keep endpoint screening identified as sampled, with event resolution still pending. |
| 7 | Fourier bases exploit periodic smooth functions, with complex conjugate coefficients for real results | Orbital forcing can be periodic while controlled attitude is not. Do not impose periodicity on the detumbling transient. Test complex eigenvalue behavior with an equivalent real two component oscillator. |
| 8 | Least squares minimizes a specified norm and gives Gram equations | No least squares solve is required by this IVP. Avoid equating a small residual or a fitted convergence line with physical correctness. |
| 9 | Orthogonal bases diagonalize Gram systems in their particular inner product | No basis expansion solve exists in current RK4. Retain independent norm definitions and ordinary array operations. |
| 10 | Integrate the ODE over one interval; approximate slopes to obtain one step methods | Existing RK4 stages and weights agree. Explicit means each stage argument is already known; evaluating a predicted stage at t+h does not make RK4 implicit. Keep four calls per step and a shortened endpoint. |
| 11 | Substitute exact solutions into the method and divide residual by h; separate new and inherited error | Explicitly distinguish the one step defect O(h^5), lecture normalized truncation error O(h^4), and global error O(h^4). Add independent one step evidence. The Adams moment conditions do not prove nonlinear RK4 order; retain the eight RK order conditions. |
| 12 | Linearize to a Jacobian, diagonalize when possible, test R(h lambda) | Add an RK4 amplification function and frozen linear diagnostics, plus the lecture's -2 and -2000 mode fixture. Strict decay is abs(R)<1; equality is marginal. Explain the negative real boundary near -2.785 and imaginary boundary at plus/minus 2 sqrt(2). |
| 13 | A fast mode can force stability steps smaller than accuracy needs; implicit/BDF methods address stiffness | Retain RK4 as the assigned method. Add a diagnostic for nonzero eigenvalue magnitude ratios and separately count neutral and growing modes. Real trajectory spectra, gain sweeps and accuracy costs remain necessary before classifying the full model. Do not silently switch to BDF or a library solver. |
| 14 | BVP finite differences solve simultaneous spatial equations; grid norms include the interval width | Carry the weighting idea into time error norms using actual sample intervals. No spatial BVP has been posed by this project. |
| 15 | Consistency and bounded error propagation jointly determine convergence; boundary accuracy matters | Keep exact solution comparisons separate from stability checks. The analogy motivates checking threshold sampling and saturation separately; it does not prove their accuracy. |
| 16 | Galerkin residual orthogonality and weak forms lead to energy norm approximation of BVPs | The spacecraft model has no distributed elastic field to discretize. Existing energy and inertial momentum invariants remain useful independent tests. They are not Galerkin error estimates. |
| 17 | Nonhomogeneous and natural boundary conditions alter trial spaces and weak forms | No boundary data at two times are specified here. Retain the initial state and forward integration rather than invent terminal conditions. |
| 18 | Local finite element bases yield sparse matrices; interfaces can limit global regularity | Smoothness matters at saturation, so smooth fourth order claims remain confined to smooth verification cases. No structural mesh is needed for rigid body attitude. |
| 19 | Beam bending requires C1 cubic Hermite basis; derivatives converge at different rates from values | This baseline assumes rigid inertia, not a flexible beam. The broader lesson is to assess actual outputs separately: accurate attitude does not establish peak torque or hold event accuracy. |

## Mathematical clarification

Write Phi_h(t,y) for one unprojected RK4 step. Starting with the exact state, define d_n=y(t+h)-Phi_h(t,y(t)). Lecture 11 uses tau_n=d_n/h. Thus d_n=O(h^5) and tau_n=O(h^4) are consistent. Under the stated smoothness and propagation assumptions the error over a fixed time interval is O(h^4). Completed quaternion projection preserves order near unit quaternions but is not included in the scalar linear stability polynomial.

RK4 has R(z)=1+z+z^2/2+z^3/6+z^4/24. On the lecture's frozen Jacobian A=[[-2,0],[400,-2000]], the eigenvalues have magnitude ratio 1000. At h=0.001 the fast z=-2 gives R=1/3; at h=0.0015 the fast z=-3 gives R=1.375. One decaying physical mode therefore grows numerically in the latter run. The supplied fixture starts in the fast eigenvector and exposes that growth. It is a verification example, not a spacecraft prediction.

A frozen eigenvalue test is local and conditional. Time dependence, nonnormal eigenvectors, neutral quaternion directions, state projection and nonsmooth saturation limit its conclusions. A nonzero mode ratio alone does not establish that the trajectory is stiff. The physical Jacobian must be assessed at relevant states and controller gains, with attention to tangent perturbations on the quaternion manifold and to coordinate scaling. This remains pending with the production field and controller.

The added L2 norm is sqrt(trapezoid(e(t)^2,t)); the maximum is the largest sampled error. Time weights prevent changing the number of samples from changing the meaning of the norm. For quaternion histories e(t) is the sign invariant attitude angle, not a raw difference in mixed physical units. These are quadrature and sample approximations, not bounds on the entire continuous trajectory.

## Changes and evidence

1. src/integrators.py retains its RK4 advancement formula and now rejects complex states or derivatives explicitly, preventing silent imaginary part loss. Complex stability modes use an equivalent real system.
2. src/numerical_analysis.py provides trajectory norms, the complex amplification polynomial and frozen linear diagnostics.
3. studies/convergence.py stores the two additional history error measurements while retaining the existing endpoint errors and plot.
4. studies/lecture_validation.py records five one step refinements and two fast mode runs with their exact reference and full fixture settings. It generates a report subsection through a separate LaTeX template.
5. report/sections/method.tex states the lecture's error convention and separates strict decay, marginal boundaries and stiffness assessment. The report includes the new measured lecture checks and copyable source.
6. Six additional tests exercise the lecture ideas and input behavior. The complete suite passes 204 tests. run_all.py completes and regenerates the numerical artifacts. Temporary test paths were directed into this workspace because the previous Windows temporary test folder was inaccessible.

The finest existing endpoint convergence orders remain 3.9899 for the scalar case and 3.9998 for rotation. See data/processed/lecture_validation.json for the measured single step defect orders and both stability runs. No production step, full model stiffness classification or full model detumbling result is claimed. LaTeX compilation remains unverified. Earlier clean clone records refer to their named historical commits, not this local revision.

## Local delivery

These edits are on aleksandar and have not been pushed. The local base is the previously published commit 07fb961. The original team modules and completed numerical results were reviewed against the applicable lecture ideas; an unrelated finite element or implicit solver rewrite would change the assigned problem and method without evidence that it is necessary.

## Source fingerprints

1. lecture-10-ivps-and-one-step-methods.html SHA256 1cdffda9e6167088b2fc8b232d3081f1ea128dd0d5034af793cda5f398a5d4f1
1. lecture-11-multi-step-methods-and-truncation-error.html SHA256 a771154716f769b4edf5ef692f83ab697430332b9d12499436a223f182d743b6
1. lecture-12-absolute-stability.html SHA256 b09e613b82cf6acd0c2b78511ef2fbef11f6c71904d7b9d2f0b6f64cc8ac37eb
1. lecture-13-stiff-ivps.html SHA256 30fce84d0c7432c3ecac5ab63728efc005647420fb84fd1160f45a88d83b6296
1. lecture-14-bvps-and-finite-differences.html SHA256 810e9552cae09cc7bfa2146797cb33c01796c3e64a9c9b0e7315d148b782441c
1. lecture-15-error-in-finite-difference-methods-for-bvps.html SHA256 23dab3025c3397ed16f55bba4d3257ab5d9cc1d6411022b2a468afb6dd15711c
1. lecture-16-global-spectral-methods-for-bvps.html SHA256 321a64da09224e7bfd5e589593c74a403eb1db11b9817e4b6c5d9affcb544f49
1. lecture-17-more-global-spectral-methods-for-bvps.html SHA256 40b422c0b9746928a65cf7a5bc8a0668b665c1beba9e6fd5ea53b9839e1711d6
1. lecture-18-finite-element-methods-for-bvps-1.html SHA256 2cefe1f045fd28849c117e62eed1e3c55c0f5a1bfeaf782219f4fe89c464bad7
1. lecture-18-finite-element-methods-for-bvps.html SHA256 2cefe1f045fd28849c117e62eed1e3c55c0f5a1bfeaf782219f4fe89c464bad7
1. lecture-19-finite-elements-for-beams.html SHA256 f04d4a4d91b8e1c4a4c054560d28b09a143b7c3613805a5324cea97a6e62e535
1. lecture-2-vector-spaces-and-subspaces.html SHA256 3d0ce5ea8e16084b421649c6f4dde5a6bc24b7a48bdc0ed2d5b611f5641476cc
1. lecture-3-norms-and-function-approximation.html SHA256 4f36b6a446ba3068f2d7696f74f01ff5c2b140ca1724727d06265ec368a4b8ec
1. lecture-4-bases-and-interpolation.html SHA256 234488d224fb5665981dfd0e99737c89248ee733b2b7bceba44d7ffdf40690d5
1. lecture-5-chebyshev-points-and-the-bad-monomial-basis.html SHA256 fcbbc9b552ab61f40af3c3e04002e87c9e8b05abe87324f54b88262d2a393e56
1. lecture-6-cubic-splines.html SHA256 8f1fe353206b550057c687bdba8182b841757cd3ab2eb09470a364f7e809ede1
1. lecture-7-trigonometric-interpolation.html SHA256 5b8bd83ea4dba1df76f1e1785cb218e4431b08a66b66328d63813850ad6fe1b2
1. lecture-8-least-squares-approximation.html SHA256 d9a84d4b8e1131cd302593b5b259859adc190b1490f59a1d33769a17c0559993
1. lecture-9-orthogonal-bases.html SHA256 c3ce0b6e194ef838103e7bd636a24317fa65c17e4830064a5d580798ef22f7d6
