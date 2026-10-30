# CubeSat Detumbling with Magnetorquers

AE 370 Aerospace Numerical Methods Fall 2026 Project 1

## Current status

Person 1 workchunks 1 and 2 are complete. The engineering premise is in `report/sections/premise.tex`. It defines the question, full initial value problem, numerical motivation, assumptions, actuator constraint, and deadline criterion. Quaternion utilities and their independent geometry tests are implemented. All numerical values remain proposed study inputs.

The repository contains the agreed folder structure and a local development environment. Dynamics and control modules, the numerical integrator, convergence drivers, engineering studies, and results remain pending. There is no reproduction runner yet. No simulation or convergence claim is made by this repository state.

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
2. `tests` holds independent correctness checks. `tests/test_quaternion.py` contains 62 passing quaternion cases.
3. `studies` holds convergence, time step selection, engineering sweeps, and figure drivers. Person 2 owns numerical studies and Person 4 owns engineering studies. This folder is currently reserved.
4. `configs` holds recorded parameters and initial conditions once implemented.
5. `data/processed` holds reproducible case records once generated.
6. `figures` holds generated report figures once available.
7. `report` holds the Overleaf source. Person 1 owns the premise and report assembly. The current main document previews the premise, quaternion verification, and the reference.

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

The observed result is 62 passing tests. These are algebraic and geometry checks. They do not establish time integration accuracy or convergence.

## Overleaf

Upload the contents of `report` to a new Overleaf project and select `main.tex` as the main document. The source uses standard packages and BibTeX. The engineering premise can also be copied from `report/sections/premise.tex` into the shared report with `\input{sections/premise}`. The shared report must include the `nasa_gnc` entry from `report/references.bib` and load `amsmath`, `amssymb`, and `hyperref`.

The current preview is not the final submission. It contains no results or completed verification studies.

## Reproducibility required before submission

The code repository is [available on GitHub](https://github.com/Yuvraj-Agarwal-101/CubeSat-Detumbling-with-Magnetorquers).

Person 4 must add exact commands for independent tests, convergence, time step selection, engineering sweeps, and figure generation as those components become available. Add a top level `run_all.py` that recreates the actual report results. Associate each figure and table with its script, configuration, seed set, and stored data. Record expected outputs and runtime.

Before submission, a teammate must follow only this README in a clean clone and regenerate all report results. Record the tested commit, verify evaluator access, and include a clickable repository link and the tested commit in the final report. These checks remain pending.

## Current report contribution

See `report/WORKCHUNK_1.md` and `report/WORKCHUNK_2.md` for scope, provenance, checks, pending work, and AI usage records. Copyable report source for workchunk 2 is in `report/sections/quaternion_verification.tex`.
