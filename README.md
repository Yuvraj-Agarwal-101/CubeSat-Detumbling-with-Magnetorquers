# CubeSat Detumbling with Magnetorquers

AE 370 Aerospace Numerical Methods Fall 2026 Project 1

## Shared team project

This repository is the common code and report repository for all four team members. The engineering question is how initial angular rate, B dot controller gain, and magnetic dipole capability affect CubeSat detumbling time and success before a mission deadline in an orbital magnetic field.

The full project includes attitude dynamics, magnetic forcing and control, a numerical integrator implemented from scratch, independent verification, convergence studies, engineering experiments, and the shared Overleaf report. Each member contributes their assigned modules, tests, study scripts, report sections, and reproduction instructions here.

`main` is the shared integration branch. Clone the repository and start from the latest `main`. Develop new tasks on descriptive branches and bring completed, checked work back into `main`. Keep reusable modules separate from tests and study scripts. Preserve the agreed quaternion convention, units, and interfaces when connecting modules.

## Current status

The engineering premise, quaternion utilities, and Euler dynamics layer are implemented. The premise is in `report/sections/premise.tex`. It defines the question, full initial value problem, numerical motivation, assumptions, actuator constraint, and deadline criterion. Independent quaternion and dynamics checks pass. All numerical values remain proposed study inputs.

The repository contains the agreed folder structure and a local development environment. Dynamics accepts explicit field and controller callbacks, but the production field and controller modules are not yet present. Production field and control, the final shared configuration, numerical integrator, convergence drivers, and engineering results remain pending. Person 4 metrics, study runners, plotting and run_all.py are implemented with synthetic pipeline checks. No full physics simulation or convergence claim is made.

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
2. `tests` holds independent correctness checks. `tests/test_quaternion.py` contains 62 quaternion cases and `tests/test_dynamics.py` contains 62 dynamics cases. All 124 cases pass.
3. `studies` holds convergence, time step selection, engineering sweeps, and figure drivers. Person 2 owns numerical studies and Person 4 owns engineering studies. Person 4 engineering drivers are implemented; numerical drivers remain pending.
4. `configs` holds recorded parameters and initial conditions once implemented.
5. `data/processed` holds reproducible case records once generated.
6. `figures` holds generated report figures once available.
7. `report` holds the Overleaf source. Person 1 owns the premise and report assembly. The current main document previews the premise, quaternion and dynamics verification, and the reference.

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

The observed result is 124 passing tests. These are instantaneous algebraic, geometry, and interface checks. They do not establish time integration accuracy or convergence.

## Dynamics API

Import `angular_acceleration` and `rhs` from `src.dynamics`. The reusable derivative has signature `rhs(t, y, config)`. State order is the four scalar first quaternion components followed by three body angular velocity components. It returns seven derivatives without advancing time.

The configuration must supply `inertia`, `field_model`, and `controller`. The inertia is a symmetric positive definite matrix of shape `(3, 3)`. The field and controller are pure callbacks, evaluated on every derivative call. Dynamics transforms the field and its derivative into body components and solves Euler's equation using the independently computed magnetic torque.

See `docs/dynamics_interface.md` for exact callback signatures, units, output keys, validation, and integration instructions. The documented contract is ready for Person 3's modules, but production integration remains pending. Tests use labeled artificial callbacks only. Missing callbacks fail explicitly.

## Overleaf

Upload the contents of `report` to a new Overleaf project and select `main.tex` as the main document. The source uses standard packages and BibTeX. The engineering premise can also be copied from `report/sections/premise.tex` into the shared report with `\input{sections/premise}`. The shared report must include the `nasa_gnc` entry from `report/references.bib` and load `amsmath`, `amssymb`, and `hyperref`.

The current preview contains the premise and completed quaternion and dynamics checks. Both verification fragments sit under Correct implementation and verification. Integration convergence, full model verification, and engineering results remain pending. The final report will combine every member's contributions.

## Reproducibility required before submission

The code repository is [available on GitHub](https://github.com/Yuvraj-Agarwal-101/CubeSat-Detumbling-with-Magnetorquers).

Person 4 must add exact commands for independent tests, convergence, time step selection, engineering sweeps, and figure generation as those components become available. Add a top level `run_all.py` that recreates the actual report results. Associate each figure and table with its script, configuration, seed set, and stored data. Record expected outputs and runtime.

Before submission, a teammate must follow only this README in a clean clone and regenerate all report results. Record the tested commit, verify evaluator access, and include a clickable repository link and the tested commit in the final report. These checks remain pending.

## Team progress records

Each member should record completed work, checks, dependencies, and AI use as their contributions are added. The existing records in `report/WORKCHUNK_1.md`, `report/WORKCHUNK_2.md`, and `report/WORKCHUNK_3.md` document the premise, quaternion, and dynamics contributions. Copyable report fragments are in `report/sections`. These records describe individual contributions within the shared project rather than limiting the repository's scope.


## Person 4 implementation and commands

The checked implementation includes metrics, deterministic ensembles, persisted case records and histories, production evidence gates, grayscale maps, gain comparisons, paired field plots, report fragments, and a figure manifest. See `report/PERSON4_HANDOFF.md` for the physics adapter contract and exact metric conventions. Ownership of other members' modules is preserved.

The Person 4 check used Python 3.13.14, NumPy 2.3.2, Matplotlib 3.10.5, and pytest 8.4.2 on Windows. `requirements-person4-tested.txt` records those direct versions separately from the team's macOS lock. Create a clean virtual environment and install one compatible environment. On Windows use `.venv\Scripts\python` instead of `.venv/bin/python` in subsequent commands.

```sh
python -m venv .venv
.venv/bin/python -m pip install -r requirements-person4-tested.txt
.venv/bin/python -m pip check
.venv/bin/python -m pytest -q -p no:cacheprovider
.venv/bin/python run_all.py --demo
```

Observed checks are recorded in `report/PERSON4_VERIFICATION.md`. Demonstration mode runs 18 orbital and 36 paired synthetic cases, retaining outputs under `data/processed/synthetic_demo`. It creates JSONL records, `.npz` histories, summary JSON, figure manifests, PDF and PNG figures, and paired outcome records. Each synthetic figure is explicitly labeled. This is a pipeline demonstration rather than the submitted engineering study. Output paths are protected against overwrite; choose a new `--output` directory to rerun.

### Real engineering workflow after upstream integration

1. Finalize `configs/study.json` assumptions with Person 1. The deadline currently uses six circular periods from radius 6871000 m and gravitational parameter 3.986004418e14 m³/s². Recompute the common deadline if these assumptions change. Match `configs/paired.json` except for field modes. The sampled initial attitudes are uniform on SO(3) via normalized Gaussian four-vectors. Spin directions are uniform on the sphere via normalized Gaussian three-vectors. Orbital phase is uniform on [0, 2 pi). Seed 3702026 is fixed. Geometries are shared across all settings and field modes.
2. Connect the physics and scratch RK4 through the documented adapter. Commit the integration. Person 2 supplies convergence, independent checks, output-grid refinement evidence, and an accepted step. `studies/convergence.py` and `studies/timestep_selection.py` are reserved for Person 2 and are not supplied by this contribution. Their executable commands must be added when those drivers exist. No external integrator is used by Person 4.
3. Copy `configs/verification.example.json` to `configs/verification.json` and record actual evidence, its SHA256 digests, accepted step, adapter, tested commit and reviewer. Do not set completion flags for pending checks. Run the 108-case pilot using the command below.
4. Review the pilot summary runtime and accuracy before production. Add its records path to verification.json. The tentative production grid has 1152 orbital cases. The paired grid has 216 cases. The same deadline is used for all cases. Synthetic runtime estimates do not estimate physics runtime.
5. Run production and paired studies, regenerate figures and tables, then copy the verified PDFs into `report/figures`. Replace pending report text with measured engineering interpretations. The full runner executes tests, production, paired studies, and figure generation. It relies on previously supplied numerical verification evidence rather than inventing Person 2's studies.

```sh
python -m studies.parameter_sweep --grid pilot --verification configs/verification.json --output data/processed/pilot/records.jsonl
python run_all.py --verification configs/verification.json
python -m studies.make_figures --records data/processed/production/records.jsonl --output figures/production
python -m studies.make_figures --records data/processed/production/paired.jsonl --output figures/paired
```

Every case stores all physical parameters, initial conditions, seed, step, configuration hash, tested commit, elapsed runtime, metrics and failure reason. Histories contain the full deadline interval. Interrupted JSONL runs retain completed records but do not currently resume automatically. Use a new output path for a restart. Invalid simulations are reported separately from right-censored deadline failures. Group success fractions show their valid denominator and invalid count. Time medians are conditional on success. No unconditional finite median is inferred from censored cases. Saturation fractions use time-weighted linearly interpolated raw norms; effort is actuator activity, not electrical energy.

The plots and `summary_table.json` report results for each gain, spin and dipole limit. `paired_outcomes.json` retains unsuccessful and invalid pairs, beyond the scatter conditional on success in both fields. Generated `manifest.json` files record generating commands, data paths, seeds and configuration hashes. The handoff includes a report figure table. Paths are repository relative when the documented commands are used. Figure regeneration needs only saved JSONL records; compressed histories permit metric audits and reanalysis.

### Final reproduction status

A clean clone reproduction of the completed physics study, final tested commit, evaluator access, real pilot runtime and production runtime remain pending. The supplied GitHub repository was cloned successfully at base commit 79161bc. The Person 4 implementation is maintained on branch `person4-experiments`. Final publication must include the implementation, accepted configuration, verification evidence and either processed data or executable generation steps for all report figures. Do not include the ignored synthetic fixture directory as engineering evidence.
