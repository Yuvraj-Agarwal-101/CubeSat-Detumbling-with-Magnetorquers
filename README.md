# CubeSat Detumbling with Magnetorquers

AE 370 Aerospace Numerical Methods Fall 2026 Project 1

## Shared team project

This repository is the common code and report repository for all four team members. The engineering question is how initial angular rate, B dot controller gain, and magnetic dipole capability affect CubeSat detumbling time and success before a mission deadline in an orbital magnetic field.

The full project includes attitude dynamics, magnetic forcing and control, a numerical integrator implemented from scratch, independent verification, convergence studies, engineering experiments, and the shared Overleaf report. Each member contributes their assigned modules, tests, study scripts, report sections, and reproduction instructions here.

`main` is the shared integration branch. Clone the repository and start from the latest `main`. Develop new tasks on descriptive branches and bring completed, checked work back into `main`. Keep reusable modules separate from tests and study scripts. Preserve the agreed quaternion convention, units, and interfaces when connecting modules.

## Current status

The engineering premise, quaternion utilities, Euler dynamics, generic classical RK4, and independent exact solution convergence studies are implemented. The premise is in `report/sections/premise.tex`. It defines the question, full initial value problem, numerical motivation, assumptions, actuator constraint, and deadline criterion. The combined suite has 204 passing tests. All engineering baseline values remain proposed study inputs.

The canonical shared configuration is now available in configs/baseline.json. The production field and controller modules are still missing. Consequently full detumbling runs, production step selection, and engineering sweeps remain pending. `run_all.py` regenerates the completed numerical contribution and explicitly records the full model step study as pending. The delivered convergence results use known scalar and spherical torque free solutions. Integration checks additionally connect RK4 to the actual dynamics with artificial zero torque callbacks. They do not substitute for production control verification.

## Local environment

The current numerical contribution was checked in a fresh Python 3.12.14 environment on Windows with NumPy 2.0.2, Matplotlib 3.9.4, and pytest 8.4.2. The following commands create a compatible environment and install the direct dependencies.

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m pip check
```

On Windows use `python` instead of `python3` and `.venv\Scripts\python.exe` instead of `.venv/bin/python`. `requirements-python312.lock` records the complete freshly tested Python 3.12 Windows environment. For exact reproduction install that file instead of `requirements.txt`. The original `requirements.lock` preserves the earlier Python 3.9.6 macOS setup. Other platforms and interpreter versions require their own compatibility check. The local `.venv` is ignored by Git.

## Organization and ownership

1. `src` holds reusable numerical and physics modules. Person 1 owns quaternion utilities and dynamics. Person 2 owns the integrator. Person 3 owns orbital forcing and control.
2. `tests` holds 62 quaternion cases, 62 instantaneous dynamics cases, 50 configuration cases, one canonical report table check, 20 integrator and study metric cases, and three integration checks. All 204 pass. Artificial fixtures are labeled explicitly.
3. `studies` holds `convergence.py`, `timestep_selection.py`, `make_figures.py`, and report generation. Person 2 owns numerical studies. Person 4's `parameter_sweep.py` and engineering figure generation remain pending.
4. `configs` holds exact verification inputs and proposed refinement settings. The canonical baseline and per-parameter provenance are in configs/baseline.json. All engineering inputs remain preliminary and the production step is unset.
5. `data/processed` holds convergence CSV and JSON, test evidence, environment metadata and the step selection status.
6. `figures` holds the monochrome convergence PDF and PNG.
7. `report` holds the shared `main.tex`, section fragments, bibliography, workchunk records and copyable Person 2 fragments. Person 1 owns final assembly.
8. `docs` holds callback interfaces and the extracted Person 2 handoff. Supporting material is kept out of reusable modules.

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

The observed result is 204 passing tests. The 175 teammate checks cover instantaneous algebra, geometry, interfaces, configuration and report consistency. The new checks add exact solution convergence and integration behavior. Production detumbling accuracy is not established by these tests.

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

Upload `report` and `figures` to Overleaf while retaining the repository layout, then select `report/main.tex` as the main document. Compile locally from the `report` directory. Alternatively upload the contents of `report` at the Overleaf root, add a root `figures` folder, and change the figure path in `sections/numerical_verification.tex` from `../figures/convergence.pdf` to `figures/convergence.pdf`. The source uses standard packages and BibTeX. Preserve the `nasa_gnc` entry in `references.bib`. The main file loads `amsmath`, `amssymb`, `graphicx`, and `hyperref`.

The shared preview includes premise, method, quaternion and dynamics checks, measured numerical convergence, reproducibility status and acknowledgments. `report/PERSON2_FRAGMENTS.md` contains copyable LaTeX source in separate fenced blocks. `report/main_preview.tex` is an optional Person 2 preview, not another final report. LaTeX compilation remains unverified in this environment. Full model verification and engineering results remain pending.

## Regenerate the delivered numerical results

Run from the repository root with the prepared environment

```sh
python -m pytest -q
python -m studies.convergence
python -m studies.make_figures
python -m studies.report_fragments
python -m studies.timestep_selection
python run_all.py
```

Use the environment's Python executable where `python` is shown. `run_all.py` regenerates the canonical baseline report table, then runs all tests and each numerical generation command in order. It creates `data/processed/test_results.txt`, `convergence.csv`, `convergence.json`, `timestep_selection.json`, `run_summary.json`, `figures/convergence.pdf`, `figures/convergence.png`, and the numerical report fragment. The exact problems use six step sizes each and no random sampling, so seeds are explicitly null. Complete configuration and initial conditions are stored in the JSON. Runtime is recorded in `run_summary.json`; allow seconds to tens of seconds on a typical computer. Full model runtime has not been measured.

The finest observed orders are approximately 3.99 for the scalar problem and 4.00 for quaternion attitude. This is the full delivered verification study, not a reduced demonstration presented as a completed engineering sweep. `manifest.json` links the figure and table to their script, configuration, seeds and data.

## Connect the production model

Read `docs/person2_interface.md` and `studies/adapter_template.py`. Supply a `team_adapter.py` implementing `build_cases()` with real unsaturated and saturated cases. Runtime `config` comes from `src.config.runtime_config` and contains the callable field and controller required by `src.dynamics.rhs`. The dipole limit is `config["controller_settings"]["max_dipole_a_m2"]`. A separate JSON compatible `config_record` stores the canonical validated case document. `callback_identifiers` stores the import paths of the real field and controller functions. Diagnostics use the shared controller keys `raw_dipole`, `dipole`, and `torque`.

```sh
python -m studies.timestep_selection --adapter team_adapter
python run_all.py --adapter team_adapter
```

The proposed settings in `configs/timestep_selection.json` must be reviewed before production. The selection gate compares each step with the next two refinements, requires unchanged success classification and both saturation regimes, and requires at least one successful case to assess detumbling timing. Sampling error in hold detection, saturation fraction and peak torque remains separate from integration error. All full model cases run for six orbital periods. Missing detumbling times stay null. A deadline failure does not prove that eventual recovery is impossible.

## Reproducibility required before submission

The code repository is [available on GitHub](https://github.com/Yuvraj-Agarwal-101/CubeSat-Detumbling-with-Magnetorquers).

The delivered tests, convergence, figure, and step study connection point now have the exact commands above. Person 4 must extend `run_all.py` and `manifest.json` when the engineering sweeps and figures are implemented. No nonexistent sweep command or fabricated engineering result is included.

Before submission, a teammate must follow only this README in a clean clone and regenerate all report results. Record the tested commit, verify evaluator access, and include a clickable repository link and the tested commit in the final report. These checks remain pending.

## Team progress records

Each member should record completed work, checks, dependencies, and AI use as their contributions are added. `report/WORKCHUNK_1.md` through `report/WORKCHUNK_4.md` and the teammate record `report/WORKCHUNKS_4_TO_6.md` document the premise, quaternion, dynamics, and numerical contributions. Copyable report fragments are in `report/sections`. These records describe individual contributions within the shared project rather than limiting the repository's scope. Final student contribution percentages have not been assigned by the agent.

Runtime and platform metadata vary across runs. Compare numerical convergence values and report content rather than requiring identical timing logs or image metadata. SHA256SUMS.txt is the committed file snapshot, not a promise that regenerated runtime logs are byte identical.

The agent reproduced all 204 tests, the numerical data, both generated tables and both figure files from a clean local Git clone of commit `02666f0e5645b83c10c65d8c1591b70d61c1fc71`. See `data/processed/clean_clone_verification.json`. This does not replace the independent teammate check or the final full project reproduction.

## Local lecture review

The followup on branch aleksandar uses the provided AE 370 Lectures 2 through 19. See docs/lecture_review.md for the mathematical comparison and changes. No remote publication is part of this review. Run python -m studies.lecture_validation for the one step defect and frozen linear stability examples; python run_all.py includes that command. There are six additional lecture checks and the current suite has 204 tests. The clean clone evidence for commit 02666f0 remains historical evidence for the earlier version, not for these local edits.
