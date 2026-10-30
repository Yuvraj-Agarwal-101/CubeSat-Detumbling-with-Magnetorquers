# Extracted project information

Source is the eight page document titled Person 2 Handoff, CubeSat Detumbling with Magnetorquers, Numerical method and convergence, AE 370 Fall 2026 Project 1.

## Authorized scope

The user's request is to extract the information and follow the document's instructions. The document assigns the coding agent the Person 2 contribution. Shared assignment requirements describe the final team deliverable and do not imply that unavailable teammate work has been completed. Target workload is 25 percent, but final percentages must reflect actual work. The current package completes the independent numerical methods work and identifies dependencies explicitly.

## Engineering question and model

Study how initial angular rate, controller gain, and magnetic dipole limit affect CubeSat detumbling time in an orbital magnetic field. The baseline is a rigid body with constant positive definite inertia, analytic circular orbit, rotating tilted dipole Earth field, ideal continuous normalized B dot control, and vector norm actuator saturation. Disturbance torques, noise, detailed field models and orbit perturbations are excluded. Sampled control is optional after baseline verification.

Use SI units and state order

\[
y=(q_0,q_1,q_2,q_3,\omega_1,\omega_2,\omega_3)^T.
\]

For scalar first quaternion \(q=(s,v)\), inertial to body rotation is

\[
C_{BI}=(s^2-v^Tv)I+2vv^T-2s[v]_\times,
\quad \dot s=-\tfrac12v^T\omega,
\quad \dot v=\tfrac12(s\omega+v\times\omega).
\]

Identity quaternion gives the identity matrix. A positive quarter turn about axis three maps inertial axis one to negative body axis two. This convention was visually checked against page 2 and tested in an independent fixture.

\[
\dot\omega=J^{-1}\{m\times B_B-\omega\times(J\omega)\},
\quad B_B=C_{BI}B_I(t),
\quad \dot B_B=C_{BI}\dot B_I(t)-\omega\times B_B,
\quad m_{raw}=-k_B\dot B_B/\|B_B\|^2.
\]

The normalized gain has units kg m^2/s and is not interchangeable with an unnormalized B dot gain. Limit the total vector norm of m to mmax. Return zero safely for zero command. Do not apply individual axis clipping.

## Preliminary assumptions

| Quantity | Proposed value |
| --- | --- |
| Inertia | diag(0.030, 0.035, 0.007) kg m^2 |
| Altitude | 500 km |
| Inclination | 55 degrees |
| Initial node and phase | Both zero |
| Initial attitude | Identity |
| Initial rate magnitude | 10 degrees/s |
| Initial rate direction | (1,1,1)/sqrt(3) |
| Pilot dipole limit | 0.1 A m^2 |
| Pilot normalized gain | 0.00001 kg m^2/s |
| Rate threshold | 0.5 degrees/s |
| Hold duration | 600 s |
| Deadline | Six orbital periods |

These are assumptions, not measured hardware values. Person 1 must confirm configuration and sources before production. The handoff does not give all orbital and magnetic constants needed for a unique full model implementation.

## Metrics

1. Detumbling time is the earliest start of a complete continuous 600 second interval below the rate threshold. The entire interval must end by the deadline.
2. Missing qualifying intervals have absent times and false success flags. Do not replace missing times with a finite recovery time.
3. Saturation fraction is the time weighted fraction for which the raw dipole norm exceeds the limit.
4. Dipole effort is the integral of the commanded dipole norm and is not electrical energy.
5. Run all ensemble cases to the same deadline. Deadline failure does not imply impossible eventual recovery.

## Ownership and interfaces

| Owner | Responsibilities |
| --- | --- |
| Person 1 | quaternion.py, dynamics.py, final common configuration, equations and final report link |
| Person 2 | integrators.py, RK4 derivation, independent exact solution convergence, production step study |
| Person 3 | orbit_field.py, controller.py, inertial field and its derivative, raw and limited dipoles and torque |
| Person 4 | metrics, study runners, engineering plotting, repository organization and reproduction |

The shared derivative is rhs(t, y, config) with seven outputs. Vectors have three components. Derivatives must be deterministic and evaluate forcing and control at every stage. They must not depend on call history.

## Person 2 completion requirements

1. Implement generic RK4 directly with optional projection after completed steps, a shortened last step, deterministic output, and preprojection quaternion norm diagnostics.
2. Derive local O(h^5), global O(h^4), the stability polynomial, cost and assumptions. Do not label the actual nonlinear model nonstiff without assessing gains and rates.
3. Independently derive spherical torque free rotation and one scalar exact solution. Handle zero rate and quaternion sign ambiguity. Use a stable atan2 attitude error.
4. Run at least five step sizes at the same final time, record errors and observed orders, and generate a monochrome logarithmic plot with fourth order reference.
5. Run real smooth and saturated full model step studies. Compare success, detumbling time, final rate, peak torque and saturation fraction. Aim for less than one percent detumbling time change, use explicit absolute tolerances, and confirm acceptance across another refinement.
6. Separate saturation nonsmoothness and hold detection sampling from integrator error. Never infer equation correctness only from refined trajectory agreement.
7. Deliver method.tex, numerical verification.tex, code, tests, scripts, data, figures, commands and unresolved dependencies. Fixtures must be labeled and must not be claimed as full model tests.

## Team submission requirements

The final submission is one technical LaTeX report rendered as PDF. Grading is premise 22, method 22, correct implementation 22, results 22, contributions 6, and reproducibility 6 points. An organized GitHub repository may earn up to 3 bonus points. Due date and page limit are not given and must be confirmed separately.

Use one main.tex and separate sections for premise, method, verification, results, reproducibility, contributions and acknowledgments. Section fragments have no preamble or document environment. Use black text, ordinary equations, numbered lists, simple tables and monochrome figures. Avoid decorative elements, emojis, dashes in prose and colons in prose or headings. Do not invent results, citations, completed tests or contribution percentages.

Keep modules in src, checks in tests, drivers in studies, parameters in configs, processed results in data/processed, figures in figures and report sources in report. Include tested dependencies, README, run_all.py and a manifest mapping figures and tables to script, configuration, seed and data.

The final code repository must actually exist and be accessible to the evaluator. Include a working clickable link and tested commit identifier in the final report. A teammate must clone it into a clean directory and regenerate all figures and tables using only the README. Publication, access checks and teammate clean clone reproduction remain pending.

The acknowledgments must explain actual generative AI use. Students must review, understand and verify generated work. No other teammate files were available in the initially identified project folder. The subsequently supplied GitHub repository contained quaternion and dynamics modules, which were preserved and checked with RK4. Production orbit, field and control remain unavailable.
