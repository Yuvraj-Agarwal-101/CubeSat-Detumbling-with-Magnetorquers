# CubeSat Detumbling with Magnetorquers

AE 370 Aerospace Numerical Methods Fall 2026 Project 1

## Current status

Only Person 1 workchunk 1 is complete. The engineering premise is in `report/sections/premise.tex`. It defines the question, full initial value problem, numerical motivation, assumptions, actuator constraint, and deadline criterion. All numerical values remain proposed study inputs.

The repository contains the agreed folder structure and a local development environment. Simulation modules, tests, convergence drivers, engineering studies, and results remain pending. There is no reproduction runner yet. No simulation or convergence claim is made by this repository state.

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
2. `tests` holds independent correctness checks. This folder is currently reserved.
3. `studies` holds convergence, time step selection, engineering sweeps, and figure drivers. Person 2 owns numerical studies and Person 4 owns engineering studies. This folder is currently reserved.
4. `configs` holds recorded parameters and initial conditions once implemented.
5. `data/processed` holds reproducible case records once generated.
6. `figures` holds generated report figures once available.
7. `report` holds the Overleaf source. Person 1 owns the premise and report assembly. The current main document is a preview containing only the premise and its reference.

## Overleaf

Upload the contents of `report` to a new Overleaf project and select `main.tex` as the main document. The source uses standard packages and BibTeX. The engineering premise can also be copied from `report/sections/premise.tex` into the shared report with `\input{sections/premise}`. The shared report must include the `nasa_gnc` entry from `report/references.bib` and load `amsmath`, `amssymb`, and `hyperref`.

The current preview is not the final submission. It contains no results or completed verification studies.

## Reproducibility required before submission

The code repository is [available on GitHub](https://github.com/Yuvraj-Agarwal-101/CubeSat-Detumbling-with-Magnetorquers).

Person 4 must add exact commands for independent tests, convergence, time step selection, engineering sweeps, and figure generation as those components become available. Add a top level `run_all.py` that recreates the actual report results. Associate each figure and table with its script, configuration, seed set, and stored data. Record expected outputs and runtime.

Before submission, a teammate must follow only this README in a clean clone and regenerate all report results. Record the tested commit, verify evaluator access, and include a clickable repository link and the tested commit in the final report. These checks remain pending.

## Current report contribution

See `report/WORKCHUNK_1.md` for scope, input provenance, pending work, and the AI usage record for this contribution.
