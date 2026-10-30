# CubeSat Detumbling with Magnetorquers

AE 370 Fall 2026 Project 1. Current implementation status is recorded here; older workchunk documents preserve the state at their original revisions.

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

On Windows use .venv\Scripts\python.exe. Use the environment interpreter where python is shown. The complete suite currently has 226 tests. The recorded test log is data/processed/test_results.txt.

The quick reproduction command regenerates the canonical parameter table, exact solution and lecture verification data, convergence figure, and report fragments. It does not rerun the expensive full model refinement unless explicitly requested with the adapter option. The dedicated refinement command runs two real idealized cases to six orbital periods at each declared step. It overwrites data/processed/timestep_selection.json with measured evidence. Wall clock runtime is recorded per case and depends on the machine. No ensemble engineering sweep is claimed by these two numerical verification cases.

The unsaturated case uses a 1 A m^2 limit, and the saturated case a 0.01 A m^2 limit. These are labeled verification choices; the baseline 0.1 A m^2 assumption is unchanged. Gain, inertia, orbit and initial conditions remain canonical. Complete case inputs and callback identifiers accompany measured results. A step that passes is a numerical screening candidate for these cases, not automatic approval across all gains, rates and success boundaries.

## Interfaces

src.orbit_field.field_model(t, config) returns (B_I, dB_I_dt). src.controller.controller(t, q, omega, B_B, dB_B_dt, config) returns raw_dipole, dipole, torque and saturated. Config is built with src.config.runtime_config. See docs/field_controller_contract.md and docs/dynamics_interface.md.

team_adapter.build_cases supplies the numerical step study. team_adapter.simulate(case, dt_s) supplies the interface described in Dibyansh's PERSON4_HANDOFF.md. It returns the full horizon, state and dipole/torque histories, plus the preprojection norm diagnostic. team_adapter.rhs_for_case(t, y, case) supports Person 4's optional frozen Jacobian audit callback. The document must be a validated canonical case. Supported field modes are orbital and frozen_inertial. No unsupported mode silently substitutes a different field. This branch does not overwrite Person 4's study runner implementations.

## Numerical evidence and limits

Exact convergence remains near fourth order. The lecture review in docs/lecture_review.md explains one step defect versus normalized truncation error, trajectory norms and frozen stability diagnostics. Full model refinement records report measured success classification, detumbling time, final rate, peak torque and saturation fraction. The method for those screening metrics uses stored output samples and is described in docs/person2_interface.md. Event sampling, missed excursions, narrow saturation intervals and peak resolution require separate review, particularly near success boundaries. Missing detumbling times remain null.

The baseline production step remains unset until measured refinement results and representative ensemble boundary cases justify updating it. Final team approval, parameter sweeps, broad gain/rate/geometry validation, final contribution percentages, evaluator access and independent teammate reproduction remain team tasks. LaTeX compilation remains unverified in this environment. No completed work is attributed to another student merely because their planned module was implemented here by request.

## Organization

Reusable modules are in src; checks in tests; drivers in studies; inputs in configs; processed records in data/processed; figures in figures; LaTeX and contribution records in report. manifest.json maps report artifacts to generators and data. All code and sources are shared in the existing repository. Generated environments and caches are excluded. Earlier clean clone records identify historical commits and should not be read as validation of later source edits.

## Measured full model refinement

Six actual simulations completed, two cases at 2, 1 and 0.5 seconds, each spanning six orbits. All six met the hold criterion. The finest sampled detumbling starts were 16135 seconds (unsaturated) and 24567 seconds (saturated). The saturated final rate changed about 2.9 percent between 2 and 1 seconds, exceeding the declared one percent limit, then about 0.058 percent between 1 and 0.5 seconds. Thus no production step is accepted yet: the finer candidate requires another confirming refinement and separate event resolution. All failed numerical comparisons remain in the JSON. The unsaturated case passes both tested comparisons. See data/processed/field_control_validation.json for a concise validation record.
