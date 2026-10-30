# CubeSat Detumbling with Magnetorquers

AE 370 Aerospace Numerical Methods Fall 2026 Project 1

## Shared team project

This repository is the common code and report repository for all four team members. The engineering question is how initial angular rate, B dot controller gain, and magnetic dipole capability affect CubeSat detumbling time and success before a mission deadline in an orbital magnetic field.

The full project includes attitude dynamics, magnetic forcing and control, a numerical integrator implemented from scratch, independent verification, convergence studies, engineering experiments, and the shared Overleaf report. Each member contributes their assigned modules, tests, study scripts, report sections, and reproduction instructions here.

`main` is the shared integration branch. Clone the repository and start from the latest `main`. Develop new tasks on descriptive branches and bring completed, checked work back into `main`. Keep reusable modules separate from tests and study scripts. Preserve the agreed quaternion convention, units, and interfaces when connecting modules.

## Current status

The engineering premise, quaternion utilities, Euler dynamics layer, shared SI configuration, interface specification, and report assembly are available. The premise is in `report/sections/premise.tex`. The assembled report follows the assignment categories and identifies pending work. All numerical values remain proposed study inputs.

Dynamics accepts explicit field and controller callbacks, but the production modules and teammate acceptance are pending. The numerical integrator, convergence drivers, engineering studies, and results remain pending. The current check command reproduces available tests and configuration evidence. It does not run the future simulation pipeline. No engineering performance or numerical convergence is claimed.

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
2. `tests` holds 62 quaternion cases, 62 dynamics cases, 50 configuration cases, and one canonical report table consistency check. All 175 cases pass.
3. `studies` holds convergence, time step selection, engineering sweeps, and figure drivers. Person 2 owns numerical studies and Person 4 owns engineering studies. This folder is currently reserved.
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

The observed result is 175 passing tests. These cover instantaneous algebra, geometry, interfaces, configuration, and report consistency. They do not establish time integration accuracy or convergence.

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
