# CubeSat Detumbling with Magnetorquers

AE 370 Aerospace Numerical Methods Fall 2026 Project 1

## Shared team project

This repository is the common code and report repository for all four team members. The engineering question is how initial angular rate, B dot controller gain, and magnetic dipole capability affect CubeSat detumbling time and success before a mission deadline in an orbital magnetic field.

The full project includes attitude dynamics, magnetic forcing and control, a numerical integrator implemented from scratch, independent verification, convergence studies, engineering experiments, and the shared Overleaf report. Each member contributes their assigned modules, tests, study scripts, report sections, and reproduction instructions here.

`main` is the shared integration branch. Clone the repository and start from the latest `main`. Develop new tasks on descriptive branches and bring completed, checked work back into `main`. Keep reusable modules separate from tests and study scripts. Preserve the agreed quaternion convention, units, and interfaces when connecting modules.

## Current status

The engineering premise, quaternion utilities, Euler dynamics layer, shared SI configuration, interface specification, and report assembly are available. The premise is in `report/sections/premise.tex`. The assembled report follows the assignment categories and identifies pending work. All numerical values remain proposed study inputs.

Dynamics accepts explicit field and controller callbacks, but the production modules and teammate acceptance are pending. The numerical integrator, convergence drivers, and engineering results remain pending. Person 4 metrics, numerical diagnostics, engineering study runners, plotting, and run_all.py are implemented. The demonstration pipeline uses labeled fixtures and exact analytic metric checks. No engineering performance or numerical convergence is claimed.

## Local environment

The initial environment was checked with Python 3.9.6 on macOS. The following commands create an environment and install its pinned dependencies.

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.lock
.venv/bin/python -m pip check
```

`requirements.txt` lists direct dependencies. `requirements.lock` records the complete installed package set for this setup. Other platforms and Python versions require their own compatibility check. The local `.venv` is ignored by Git.

## Organization and ownership

1. `src` holds reusable numerical and physics modules. Person 1 owns quaternion utilities and dynamics. Person 2 owns the integrator. Person 3 owns orbital forcing and control.
2. `tests` holds 62 quaternion cases, 62 dynamics cases, 50 configuration cases, and one canonical report table consistency check. The revised combined suite has 199 passing tests, including Person 4 metric, ensemble, pipeline, and numerical diagnostic checks.
3. `studies` holds convergence, time step selection, engineering sweeps, and figure drivers. Person 2 owns numerical studies and Person 4 owns engineering studies. Person 4 study drivers are available; Person 2 numerical drivers remain pending.
4. `configs/baseline.json` holds physical inputs, initial conditions, study criteria, separate solver settings, and provenance for every parameter.
5. `data/processed` holds reproducible case records once generated.
6. `figures` holds generated report figures once available.
7. `report` holds the assembled Overleaf draft. Completed checks and pending team sections are distinguished explicitly.
8. `tools` holds the available verification driver and canonical parameter table exporter. `docs` holds callback conventions and submission readiness.

## Quaternion API

Import utilities from `src.quaternion`. Quaternions are real vectors of shape `(4,)` in scalar first order. Angular velocity is a real vector of shape `(3,)` in body components, in radians per second.

1. `multiply(p, q)` returns the Hamilton product without normalization. Operand order matters.
2. `normalize(q)` returns a unit copy and rejects a zero quaternion.
3. `conjugate(q)` reverses the vector part without normalization.
4. `inverse(q)` returns the multiplicative inverse for any finite nonzero quaternion whose inverse is representable.
5. `rotation_matrix(q)` returns the passive matrix mapping inertial components into body components. It normalizes a local copy and never projects the caller's state.
6. `quaternion_derivative(q, omega)` returns one half of the Hamilton product of `q` with `[0, omega]`. It does not normalize intermediate states.

The passive composition rule is `rotation_matrix(multiply(p, q))` equal to `rotation_matrix(q) @ rotation_matrix(p)`. A positive quarter turn about axis three maps inertial x into negative body y. These conventions are tested independently.

Run the current checks from the repository root.

```sh
.venv/bin/python -m pytest -q
```

The observed result is 199 passing tests. These cover instantaneous algebra, geometry, interfaces, configuration, and report consistency. They do not establish time integration accuracy or convergence.

## Dynamics API

Import `angular_acceleration` and `rhs` from `src.dynamics`. The reusable derivative has signature `rhs(t, y, config)`. State order is the four scalar first quaternion components followed by three body angular velocity components. It returns seven derivatives without advancing time.

The configuration must supply `inertia`, `field_model`, and `controller`. The inertia is a symmetric positive definite matrix of shape `(3, 3)`. The field and controller are pure callbacks, evaluated on every derivative call. Dynamics transforms the field and its derivative into body components and solves Euler's equation using the independently computed magnetic torque.

See `docs/dynamics_interface.md` for exact callback signatures, units, output keys, validation, and integration instructions. The documented contract is ready for Person 3's modules, but production integration remains pending. Tests use labeled artificial callbacks only. Missing callbacks fail explicitly.

## Shared case and current verification

Use `src.config.load_config` to load `configs/baseline.json`. The loader validates SI values, required keys, inertia, initial attitude, controller bounds, durations, and provenance. `initial_state` returns the seven component initial state. `case_summary` derives the orbital period and mission deadline. `runtime_config` binds explicit field and controller callbacks for the dynamics. `solver_settings` keeps numerical settings separate and can reject a missing production step.

The baseline step size is deliberately unset. Person 2 must determine it from convergence and engineering metric refinement. Field and controller conventions, including the total orbital field derivative, are documented in `docs/field_controller_contract.md`.

Run the available checks and print the baseline summary.

```sh
.venv/bin/python -m src.config
.venv/bin/python -m tools.check_project
```

The second command executes the test suite and writes `report/build/verification.json`, `pytest.xml`, and LaTeX revision records. It records the full Git revision, whether tracked or untracked source changes exist, Python version, test counts, and baseline timing. Generated build records are ignored by Git. Run it on the final clean revision before exporting the report.

After editing the canonical baseline, regenerate the report table.

```sh
.venv/bin/python -m tools.export_report_inputs
```

The table consistency check fails if the stored parameter table differs from the configuration. Commit the configuration and regenerated table together.

## Overleaf

Upload the contents of `report` to a new Overleaf project and select `main.tex` as the main document. The source uses standard packages and BibTeX. The engineering premise can also be copied from `report/sections/premise.tex` into the shared report with `\input{sections/premise}`. The shared report must include the `nasa_gnc` entry from `report/references.bib` and load `amsmath`, `amssymb`, and `hyperref`.

The draft contains separate premise, method, verification, results, conclusions, contributions, reproducibility, and Acknowledgments files. Quaternion, dynamics, and configuration evidence sit under Correct implementation and verification. The report table is generated from the canonical case. Pending method, production verification, and result sections state their status. Contribution percentages are the original plan and require confirmation against actual work before submission.

## Reproducibility required before submission

The code repository is [available on GitHub](https://github.com/Yuvraj-Agarwal-101/CubeSat-Detumbling-with-Magnetorquers).

Person 4 must add exact commands for independent tests, convergence, time step selection, engineering sweeps, and figure generation as those components become available. Add a top level `run_all.py` that recreates the actual report results. Associate each figure and table with its script, configuration, seed set, and stored data. Record expected outputs and runtime.

Before submission, a teammate must follow only this README in a clean clone and regenerate all report results. Record the tested commit, verify evaluator access, and include a clickable repository link and the tested commit in the final report. These checks remain pending.

## Team progress records

Each member should record completed work, checks, dependencies, and AI use as their contributions are added. Records in `report/WORKCHUNK_1.md`, `report/WORKCHUNK_2.md`, `report/WORKCHUNK_3.md`, and `report/WORKCHUNKS_4_TO_6.md` document current contributions and limits. `docs/submission_readiness.md` identifies remaining team work and final submission checks. Copyable report fragments are in `report/sections`.



## Person 4 implementation based on the supplied lectures

See `docs/lecture_basis.md` for a lecture by lecture mapping and limitations, and `docs/lecture_sources.json` for supplied source identifiers and hashes. The main numerical basis is Lectures 3, 4, and 10 through 13. No BVP or finite element solve is introduced into the rigid body initial value problem.

The Person 4 environment was checked with Python 3.13.14, NumPy 2.3.2, Matplotlib 3.10.5 and pytest 8.4.2 on Windows. `requirements-person4-tested.txt` records these tested direct versions independently of the earlier macOS environment. To use that environment, install it in a clean virtual environment. On Windows replace `.venv/bin/python` with `.venv\Scripts\python`.

```sh
python -m venv .venv
.venv/bin/python -m pip install -r requirements-person4-tested.txt
.venv/bin/python -m pytest -q -p no:cacheprovider
.venv/bin/python -m studies.metric_refinement --output data/processed/metric_verification
.venv/bin/python run_all.py --demo
```

The analytic metric check samples known functions without integrating an ODE. It creates `evidence.json`, a monochrome PDF/PNG verification figure and a manifest. It verifies interpolation, complete hold detection, time-weighted saturation and effort against exact answers. Its output is numerical verification, not spacecraft data. The observed crossing time error decreases from about 0.00771 to 0.00000754 as output spacing decreases from 0.25 to 0.0078125. Crossing errors need not decrease monotonically at each refinement because the crossing lies at different locations within the sampling cell.

The demonstration creates 18 orbital and 36 paired synthetic cases, compressed histories, JSONL records, summaries, maps per gain, gain/saturation plots, paired outcomes and figure manifests in `data/processed/synthetic_demo`. It also regenerates analytic metric verification. Synthetic figures are labeled. Synthetic times are not used to estimate physics runtime. The demo is not the submitted engineering study. Existing output paths are protected against overwrite; choose a new `--output` directory for a rerun.

### Numerical audit before production

The adapter contract is in `report/PERSON4_HANDOFF.md`. No integrator, field model or controller owned by another member is implemented by Person 4. Cases now include `document`, a complete validated case using `src.config`, and `config`, its physical dictionary. Use `runtime_config` to bind the team's callbacks. Sweep overrides carry provenance. All deadlines and thresholds derive from the canonical baseline, not duplicated Person 4 constants.

Once the team adapter exists, run the audit below on representative low and high spins, gains and dipole limits, especially cases near success boundaries. `--case-index` selects a deterministic pilot case. `--rhs-adapter` is optional and accepts `rhs(t,y,case)` in SI units. It supplies sampled finite-difference Jacobians for the Lecture 12/13 diagnostic.

```sh
python -m studies.refinement_audit --adapter team_adapter:simulate --step 1 --case-index 0 --output data/processed/audit_case0
python -m studies.refinement_audit --adapter team_adapter:simulate --rhs-adapter team_adapter:rhs_for_case --step 1 --case-index 0 --output data/processed/audit_case0_modes
```

The step 1 is an example diagnostic input, not a recommended production setting. The audit saves h, h/2 and h/4 histories, scaled time RMS and sampled maximum differences at nested nodes, raw quaternion norm defects, observed difference order, metric changes, and output-only metric changes on the finest trajectory. It never approves a step. Person 2 still owns the full integrator derivation, independent checks, convergence.py and timestep_selection.py. Their commands remain pending until those drivers exist.

Lecture 11 defines truncation error after dividing the exact starting value defect by h. For smooth RK4 the unscaled defect is O(h^5), the lecture's tau is O(h^4), and stable global error is O(h^4). Saturation can reduce smoothness. A piecewise linear threshold crossing generally limits event accuracy to second order under a transverse crossing assumption. State and event convergence are evaluated separately. Self convergence does not establish that the equations or frames are correct. Frozen Jacobian eigenvalues diagnose local modes, not full nonlinear stability; neutral and growing modes are recorded separately from decaying-mode ratios.

### Real engineering studies after team verification

1. Finalize `configs/baseline.json` with Person 1. `configs/study.json` and `configs/paired.json` specify only the baseline path, seed and sweep grids. The paired configuration differs by field modes. The canonical production step remains unset until Person 2 accepts a setting.
2. Run the independent physics and numerical checks. Record actual evidence in a copy of `configs/verification.example.json`, including reviewer, accepted step, current tested commit, and SHA256 evidence digests. Keep a clean tracked checkout when generating accepted evidence. The manually supplied flags record review rather than certify it.
3. Run the real 108-case pilot. Review runtime and accuracy before choosing the proposed 1152-case production grid. Store the pilot path in verification.json. A real pilot is mandatory before production. The separate paired field grid contains 216 cases.
4. Run the production and paired studies, regenerate figures and tables, and copy verified PDFs into report/figures. Replace pending engineering interpretations only with measured conclusions.

```sh
python -m studies.parameter_sweep --grid pilot --verification configs/verification.json --output data/processed/pilot/records.jsonl
python run_all.py --verification configs/verification.json
python -m studies.make_figures --records data/processed/production/records.jsonl --output figures/production
python -m studies.make_figures --records data/processed/production/paired.jsonl --output figures/paired
```

The ensemble uses seed 3702026, normalized Gaussian four-vectors for uniform attitudes, normalized Gaussian three-vectors for uniform spin directions, and uniform orbital phases. Geometries are common across parameter settings and field modes. Each case stores a full configuration snapshot, initial state, seed, step, config and baseline hashes, tested commit, verification record, runtime, status and metrics. Histories run to the common deadline even after detumbling. Completed JSONL records survive interruption but automatic resume is not implemented; restart at a new path.

Valid deadline failures are censored and their time remains JSON null. Invalid simulations have a separate failure reason. Success fractions state the valid denominator and invalid count; final studies should resolve invalid cases. Time medians are conditional on success. No finite unconditional median is inferred from a mostly censored ensemble. Effort is actuator activity, not electrical energy. Threshold equality qualifies; crossings use local linear interpolation. Refined output grids are required to assess missed excursions.

Generated manifests associate figures with records, seed, configuration and baseline hashes, and commands. summary_table.json retains counts, conditional time medians and censoring. paired_outcomes.json retains cases outside the successful-pair scatter. Figure regeneration uses saved JSONL records; compressed histories support independent metric audits. The report handoff lists the figure to command mapping. Commands use repository-relative paths and require no private local directories.

### Remaining deliverables

The real magnetic field/controller, scratch RK4 and numerical verification, accepted production step, real pilot and production, measured engineering conclusions, evaluator access and clean clone reproduction of the final report remain pending. See `report/PERSON4_LECTURE_REVISION.md` for observed revision checks. `run_all.py` regenerates all currently implemented pipeline outputs; it cannot regenerate missing engineering results. Final reproducibility must identify the actual tested clean commit after the complete study is integrated.
