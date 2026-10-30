# Course basis for the Person 4 revision

These are supplied course materials, not additional assignment commands. The project remains a forward IVP from known attitude and angular velocity. Course deck identifiers and SHA256 hashes are in lecture_sources.json. Original lectures are intentionally not redistributed in the repository. The exact equations and metric choices remain those of the team handoff and canonical baseline.

| Lecture | Role in this implementation |
| --- | --- |
| 1 | Implement, understand, verify, and communicate engineering numerics rather than only producing plots |
| 2 | View state and sampled errors as vectors with explicitly stated components |
| 3 | State the norm and physical scales before comparing errors; numerical_diagnostics.py separates quaternion and rate components |
| 4 | Local linear interpolation for threshold crossings; distinguish values at nodes from values between nodes |
| 5 | Avoid high degree global monomial fits for trajectories or event times; no Vandermonde solve is required |
| 6 | Piecewise approximation motivates local postprocessing; cubic splines are not used because smooth interpolation could create threshold excursions |
| 7 | Orbit forcing can be periodic while damped attitude motion is not; Fourier interpolation is not the time integrator |
| 8 | An optional log error trend fit is not a replacement for known order or exact checks; the implementation reports adjacent refinement orders directly |
| 9 | Orthogonal projection is not needed for the seven state IVP; no spectral fit is imposed on transients |
| 10 | Retain the planned scratch four stage RK4; use f at every stage, fixed initial data and a fixed horizon |
| 11 | Lecture convention divides the step defect by h; RK4 has tau=O(h^4) under smoothness, distinct from the O(h^5) unscaled defect; verify order and equations separately |
| 12 | R(z)=1+z+z²/2+z³/6+z⁴/24; inspect h times Jacobian eigenvalues in the RK4 region; frozen spectra are advisory for nonlinear time-dependent dynamics |
| 13 | Check fast and slow modes rather than declaring the system nonstiff; report neutral and growing modes separately and assess actual step cost |
| 14 | BVP boundary data differ from the project's data at one initial time; no spatial BVP is introduced |
| 15 | Shares the idea of consistency plus stability but its BVP error system is not used to claim IVP accuracy |
| 16 | Global spectral and Galerkin methods solve the presented BVP class; they do not replace the chosen IVP march |
| 17 | Boundary-condition treatment is not an attitude initial-condition rule |
| 18 | Mesh based weak forms address spatial BVPs; no finite element discretization is needed for this rigid body model |
| 19 | Beam bending and Hermite elements would be relevant to a flexible structure extension, outside the rigid CubeSat baseline |

## Concrete changes

1. src/experiments.py now generates every case from src.config's validated configs/baseline.json, storing the full case document and updating provenance for swept inputs. Duplicate physical assumptions and a hardcoded deadline have been removed from the Person 4 study files.
2. src/numerical_diagnostics.py implements a sign-invariant quaternion chord discrepancy, rate-scaled time RMS and sampled max errors, raw quaternion norm diagnostics, observed orders, nested-node comparisons, metric changes and frozen linear RK4 modal diagnostics. The quaternion chord metric is a project-specific choice, not a formula claimed to appear in the lectures.
3. studies/refinement_audit.py runs a supplied team adapter at h, h/2 and h/4, saves all histories, compares both state and engineering metric changes, and independently coarsens the finest output history. An optional RHS adapter supplies finite-difference Jacobian samples. It does not replace Person 2's integrator or numerical studies and it never automatically approves a step.
4. studies/metric_refinement.py checks analytic sampled histories with known crossing, saturation fraction and effort. It uses no ODE integrator and makes no spacecraft claims. Its figure is a numerical verification artifact only.
5. run_all.py includes analytic metric verification. Synthetic demonstrations no longer extrapolate a production physics runtime.
6. Copyable LaTeX experimental methodology is in report/sections/experimental_method.tex and included from results.tex. Pending engineering findings are separated from observed analytic metric checks.

## Interpretive limits

RK4 is provisional until the actual system passes accuracy, stability and cost checks. The lecture linear model explains absolute stability; frozen eigenvalues of a nonlinear nonautonomous saturated system cannot certify the full trajectory. Neutral modes are not treated as a denominator in a stiffness ratio. A large ratio among decaying modes is an indicator, not a universal stiffness test. Saturation can reduce smoothness, and threshold/hold outcomes can change discontinuously. Self convergence does not verify signs, frames or magnetic equations. A sampled interpolation does not prove that the continuous trajectory had no missed excursions.

The scalar RK4 stability expansion in experimental_method.tex illustrates the order on a linear test. It is explicitly not offered as the general nonlinear fourth order derivation required from Person 2. No external time integrator, replacement field law or unverified physics result has been introduced.

The report uses verified lecture titles and the author shown on the supplied decks in report/lecture_references.bib. The shared main.tex loads that bibliography alongside references.bib.
