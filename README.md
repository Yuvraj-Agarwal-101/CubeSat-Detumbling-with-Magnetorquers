# CubeSat Detumbling with Magnetorquers

AE 370 Fall 2026 Project 1. Current code is on the [aleksandar branch](https://github.com/Yuvraj-Agarwal-101/CubeSat-Detumbling-with-Magnetorquers/tree/aleksandar). Current implementation status is recorded here; older workchunk documents preserve the state at their original revisions.

## Full idealized model

The branch now implements the circular orbit and rotating tilted dipole in src/orbit_field.py, the normalized continuous B dot controller in src/controller.py, shared quaternion/Euler dynamics, and scratch RK4. src.config retains the canonical assumed parameters and provenance. No external time integrator is used.

The analytic inertial field derivative includes both orbital motion and Earth dipole rotation. Dynamics applies the body rotation term exactly once. The controller applies a bound on the total dipole vector, returns zero safely and rejects an unresolved zero magnetic field. These remain idealized study assumptions rather than measured spacecraft or epoch specific geomagnetic predictions.

Independent tests cover orbit orientation, radius and period, equatorial/polar field strength, the analytic derivative against step-refined centered differences, zero command, saturation boundaries, torque geometry, static field energy dissipation, and actual seven component dynamics wiring. Static field dissipation does not imply monotonic energy under varying orbital forcing.

## Run

From the repository root use Python 3.12 and a virtual environment. Install requirements-python312.lock for the tested Windows environment, or requirements.txt and validate compatibility for another platform.

```sh
python -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m pytest -q
python run_all.py
python -m studies.timestep_selection --adapter team_adapter --settings configs/full_model_refinement.json
```

On Windows use .venv\Scripts\python.exe. Use the environment interpreter where python is shown. The complete suite currently has 234 tests. The recorded test log is data/processed/test_results.txt.

The quick reproduction command regenerates the canonical parameter table, exact solution and lecture verification data, convergence figure, and report fragments. It does not rerun the expensive full model refinement unless explicitly requested with the adapter option. The dedicated refinement command runs two real idealized cases to six orbital periods at each declared step. It overwrites data/processed/timestep_selection.json with measured evidence. Wall clock runtime is recorded per case and depends on the machine. No ensemble engineering sweep is claimed by these two numerical verification cases.

The unsaturated case uses a 1 A m^2 limit, and the saturated case a 0.01 A m^2 limit. These are labeled verification choices; the baseline 0.1 A m^2 assumption is unchanged. Gain, inertia, orbit and initial conditions remain canonical. Complete case inputs and callback identifiers accompany measured results. A step that passes is a numerical screening candidate for these cases, not automatic approval across all gains, rates and success boundaries.

## Interfaces

src.orbit_field.field_model(t, config) returns (B_I, dB_I_dt). src.controller.controller(t, q, omega, B_B, dB_B_dt, config) returns raw_dipole, dipole, torque and saturated. Config is built with src.config.runtime_config. See docs/field_controller_contract.md and docs/dynamics_interface.md.

team_adapter.build_cases supplies the numerical step study. team_adapter.simulate(case, dt_s) supplies the interface described in Dibyansh's PERSON4_HANDOFF.md. It returns the full horizon, state and dipole/torque histories, plus the preprojection norm diagnostic. team_adapter.rhs_for_case(t, y, case) supports Person 4's optional frozen Jacobian audit callback. The document must be a validated canonical case. Supported field modes are orbital and frozen_inertial. No unsupported mode silently substitutes a different field. This branch does not overwrite Person 4's study runner implementations.

## Numerical evidence and limits

Exact convergence remains near fourth order. The lecture review in docs/lecture_review.md explains one step defect versus normalized truncation error, trajectory norms and frozen stability diagnostics. Full model refinement records report measured success classification, detumbling time, final rate, peak torque and saturation fraction. The method for those screening metrics uses stored output samples and is described in docs/person2_interface.md. Event sampling, missed excursions, narrow saturation intervals and peak resolution require separate review, particularly near success boundaries. Missing detumbling times remain null.

The baseline now records the numerically accepted 1-second step for the stated scope. Broader ensemble boundary cases require their own audit. Final team approval, parameter sweeps, broad gain/rate/geometry validation, final contribution percentages, evaluator access and independent teammate reproduction remain team tasks. LaTeX compilation remains unverified in this environment. No completed work is attributed to another student merely because their planned module was implemented here by request.

## Organization

Reusable modules are in src; checks in tests; drivers in studies; inputs in configs; processed records in data/processed; figures in figures; LaTeX and contribution records in report. manifest.json maps report artifacts to generators and data. All code and sources are shared in the existing repository. Generated environments and caches are excluded. Earlier clean clone records identify historical commits and should not be read as validation of later source edits.

## Completed Person 2 numerical verification

The canonical production step is now 1 second for the declared baseline. Both unsaturated and saturated cases pass every metric tolerance across 1 to 0.5 and 0.5 to 0.25 seconds. The failed saturated 2 to 1 second comparison is retained. Eight refinement simulations plus a separate baseline simulation span six orbits each.

The fixed-trajectory output audit coarsens quarter-second output to 0.5 and 1 second spacing. The largest change in interpolated detumbling start is about 0.000366 seconds, below the separate one-second event tolerance. The actual 0.1 A m^2 baseline bound was inactive at all 136036 evaluated RK4 stages; the maximum raw command was 0.07030255 A m^2. This connects the unsaturated reference to the canonical baseline. Reference metrics agree to roundoff rather than bitwise identity because the two projection implementations use slightly different floating point norm evaluations.

Evidence is in data/processed/production_validation/acceptance.json, confirmation.json and baseline.json. Compact scalar traces independently reproduce the output audit. Acceptance binds the evidence files and physics source through SHA256 hashes. The operational setting and report parameter table are updated together. No external numerical solver or unmeasured result is used.

The numerical implementation, derivation, exact convergence, physical checks, two successive full model refinements, output resolution and production step selection are complete for this stated scope. Wider parameter sweeps and the team's final combined submission remain separate responsibilities. Other gains, spins and geometries must be audited before extrapolating this step to a broad engineering grid.

## Full reproduction

```sh
python run_all.py
python run_all.py --complete-verification
```

The first command runs all 234 tests and regenerates the inexpensive numerical/physics evidence, figure and report fragments while preserving the costly full-model histories. The second explicitly reruns the coarser full model studies, two parallel quarter-second studies, baseline confirmation and acceptance; it then reruns the entire test suite. Allow substantial runtime, on the order of an hour on this shared Windows environment, rather than treating this as a fast demonstration. Exact runtime depends strongly on concurrency and hardware. The full study has no random cases and uses null seeds.

Low-level commands are python -m studies.timestep_selection --adapter team_adapter --settings configs/full_model_refinement.json, python -m studies.complete_verification, python -m studies.baseline_confirmation, and python -m studies.production_acceptance --apply. The continuation reuses only coarser evidence with matching source fingerprints. Its archived configuration is replayed even after the recommended solver step is updated. A physics or configuration change requires new evidence, not reuse of stale acceptance.

report/person2.tex collects the completed numerical contribution. report/main.tex is the shared team assembly. Both load the supplied lecture references in report/references.bib. The source fragments remain separately copyable. Final student review, actual contribution percentages, independent teammate reproduction and the broader engineering study are not invented by the agent.

## Report compilation

The report sources have been compiled with Tectonic 0.17.0 using standard LaTeX packages and BibTeX. From report run tectonic --untrusted person2.tex for the standalone numerical contribution, or tectonic --untrusted main.tex for the shared draft. On Overleaf upload the contents of report at the project root and add the figures directory at that root. Select person2.tex or main.tex as appropriate. The convergence figure has a repository/Overleaf path fallback, so no manual source edit is required. The standalone contribution is a component of the shared final report, not a claim that the team's engineering sweep is complete.
