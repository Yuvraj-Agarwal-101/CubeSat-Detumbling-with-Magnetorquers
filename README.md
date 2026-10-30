# CubeSat Detumbling with Magnetorquers

**AE 370 Aerospace Numerical Methods — Fall 2026 Project 1**

This project studies how the initial angular rate, normalized B-dot controller gain, magnetorquer dipole capability, and initial geometry affect CubeSat detumbling in an orbital magnetic field.

The final model combines quaternion rigid-body attitude dynamics, an idealized orbital magnetic-field model, normalized B-dot control with vector-norm actuator saturation, and a classical fourth-order Runge-Kutta integrator implemented from scratch.

## Final project status

The final integrated project is on the `main` branch.

- 311 automated tests pass.
- The accepted production timestep is **0.25 s**.
- The submitted engineering study contains **16 real targeted cases**.
- **15 cases recovered**, **1 case was censored at the six-orbit deadline**, and **0 cases were invalid**.
- Submitted recovery times range from approximately **863 s to 20,622 s** among successful cases.
- The report figures and tables are generated from committed real engineering histories.
- The larger planned 108-case pilot and 1152-case sweep were not used for the final conclusions.

## Engineering question

> How do initial angular rate, normalized B-dot controller gain, and maximum magnetic dipole moment affect the time required for a CubeSat to detumble in an orbital magnetic field?

The study also examines sensitivity to initial attitude, spin direction, and orbital phase.

A case is considered successful when the angular-rate norm remains at or below **0.5 deg/s continuously for 600 s**, with the complete hold interval ending before the six-orbit mission deadline.

## Repository organization

The repository separates reusable model and numerical code from verification and engineering-study scripts.

```text
CubeSat-Detumbling-with-Magnetorquers/
├── src/
│   ├── numerics/              # Numerical-method implementation
│   │   ├── integrators.py     # Euler, Heun, and scratch RK4
│   │   ├── errors.py
│   │   └── stability.py
│   ├── physics/               # Quaternion and rigid-body physics
│   ├── controller.py          # Normalized B-dot controller
│   ├── orbit_field.py         # Orbital magnetic-field model
│   ├── experiments.py         # Deterministic case generation
│   └── metrics.py             # Recovery and actuator metrics
│
├── studies/                   # Convergence, refinement, and study drivers
├── tests/                     # Independent automated verification
├── configs/                   # Baseline, study, and verification settings
├── docs/
│   └── pilot_validation/      # Final targeted-study reproduction tools
├── data/
│   └── processed/             # Saved numerical evidence and study records
├── figures/                   # Generated verification and engineering figures
├── report/                    # LaTeX report source
├── team_adapter.py            # Full-model simulation adapter
├── run_all.py                 # Numerical verification workflow
├── requirements.txt           # Direct Python dependencies
└── README.md
```

The numerical integration implementation is therefore separated from the programs that perform convergence studies and generate engineering results.

## Environment

The final targeted-study environment was recorded as:

- Python 3.11.6
- NumPy 2.0.2
- Matplotlib 3.9.4
- pytest 8.4.2
- Windows 64-bit

Direct dependencies are listed in `requirements.txt`.

### Clone the repository

```bash
git clone https://github.com/Yuvraj-Agarwal-101/CubeSat-Detumbling-with-Magnetorquers.git
cd CubeSat-Detumbling-with-Magnetorquers
```

### Create the environment

#### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip check
```

#### macOS / Linux

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m pip check
```

A Python 3.12 Windows environment is also recorded in `requirements-python312.lock`.

## Run the automated tests

From the repository root:

### Windows

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

### macOS / Linux

```bash
.venv/bin/python -m pytest -q
```

Expected result for the submitted project:

```text
311 passed
```

The tests cover quaternion conventions, rigid-body dynamics, numerical integration, exact-solution convergence, magnetic-field behavior, B-dot control, actuator saturation, configuration handling, numerical refinement, and merged-model interfaces.

## Reproduce numerical verification

The main numerical-verification workflow can be run with:

### Windows

```powershell
.\.venv\Scripts\python.exe run_all.py
```

### macOS / Linux

```bash
.venv/bin/python run_all.py
```

This runs the automated tests and regenerates the main numerical verification studies and associated report artifacts.

The numerical studies include:

- exact scalar decay convergence,
- spherical torque-free rotation,
- asymmetric torque-free conservation,
- RK4 stability checks,
- magnetic-field and controller verification,
- full-model numerical refinement evidence.

The accepted production timestep is **0.25 s**. Detailed Stage 3 numerical evidence is stored under `docs/stage3_validation/` and the corresponding processed verification data.

## Regenerate the submitted engineering figures and tables

The submitted engineering figures and tables can be regenerated directly from the committed real simulation histories without rerunning the expensive spacecraft integrations.

### Windows

```powershell
.\.venv\Scripts\python.exe docs\pilot_validation\build_submission.py
```

### macOS / Linux

```bash
.venv/bin/python docs/pilot_validation/build_submission.py
```

This command:

- assembles the 16 submitted real cases,
- independently validates the saved trajectories and metrics,
- regenerates the final study summary,
- regenerates the results table,
- regenerates the geometry comparison figure,
- regenerates the spin/gain comparison figure,
- regenerates the actuator comparison figure,
- updates the artifact manifest and hashes.

The main outputs are stored in:

```text
data/processed/targeted/
figures/targeted/
report/figures/
```

This command **does not run any new simulations**.

## Rerun the complete submitted 16-case engineering study

The exact 16 real simulations used in the final report can also be rerun from scratch.

This is optional because it is substantially more expensive than regenerating figures from the committed histories.

### Windows

```powershell
.\.venv\Scripts\python.exe docs\pilot_validation\run_parallel_pilot.py `
  --workers 4 `
  --indices 0,1,2,3,4,5,6,7,8,9,10,11,72,24,96,104 `
  --output data/processed/reproduction16/records.jsonl
```

### macOS / Linux

```bash
.venv/bin/python docs/pilot_validation/run_parallel_pilot.py \
  --workers 4 \
  --indices 0,1,2,3,4,5,6,7,8,9,10,11,72,24,96,104 \
  --output data/processed/reproduction16/records.jsonl
```

The runner:

- uses the real `team_adapter:simulate` model,
- uses the accepted `0.25 s` RK4 timestep,
- evaluates the real orbital field and B-dot controller,
- runs every case through the complete six-orbit deadline,
- preserves successful, censored, and invalid records,
- records configuration and runtime information,
- does not use synthetic spacecraft data.

The output path must not already exist.

Runtime depends on hardware and worker count. During the submitted study, the first 12 cases completed in approximately 408 s wall time using 12 workers, while the final four completed in approximately 241 s using four workers.

## Submitted engineering study

The final report uses a targeted 16-case study rather than an exhaustive parameter sweep.

The study contains matched comparisons involving:

- initial spin magnitude,
- normalized B-dot gain,
- magnetorquer dipole limit,
- initial geometry.

The main measured conclusions are:

- Increasing initial spin made recovery substantially more difficult in the matched cases.
- At 1 deg/s, increasing gain by a factor of ten reduced recovery time from approximately 9492 s to 863 s.
- At 30 deg/s and the higher gain, increasing the dipole limit from 0.03 to 0.3 A m² reduced recovery time from approximately 20,622 s to 8043 s.
- In that actuator comparison, saturation decreased from approximately 48.4% to 1.6%.
- Initial geometry produced substantial variation in recovery time.
- Increasing actuator capability produced no benefit when the lower actuator bound was already inactive.

These conclusions apply only to the tested parameter combinations and the idealized model used in this project.

## Numerical method

The primary production integrator is classical RK4 implemented from scratch in:

```text
src/numerics/integrators.py
```

No external ODE integrator is used to advance the submitted spacecraft trajectories.

The code separately contains:

- numerical integration routines under `src/numerics/`,
- physical dynamics and control under `src/`,
- convergence and refinement studies under `studies/`,
- independent tests under `tests/`,
- final engineering-study reproduction scripts under `docs/pilot_validation/`.

This separation allows the numerical method to be tested independently of the spacecraft model and engineering study.

## Saved evidence

Important submitted evidence includes:

```text
configs/baseline.json
configs/study.json
configs/verification.json

data/processed/targeted/
docs/stage3_validation/
docs/pilot_validation/

figures/targeted/
report/figures/
```

The final targeted-study seed is:

```text
3702026
```

Simulation records contain the case configuration, initial condition, timestep, success classification, detumbling time, saturation fraction, actuator metrics, runtime, and history location.

## Report

The LaTeX report source is stored under:

```text
report/
```

The main document is:

```text
report/main.tex
```

The submitted report contains the engineering premise, numerical method, implementation verification, engineering results, conclusions, team contributions, reproducibility instructions, and acknowledgments.

## Team

- **Yuvraj Agarwal** — spacecraft dynamics and model architecture
- **Aleksandar Bargoz** — numerical method development and verification
- **Sidhant Jha** — orbital magnetic-field and B-dot controller verification, plus final model integration
- **Dibyansh Choudhury** — recovery-event algorithms, engineering metrics, parameter-study and results pipeline

The final report records the agreed contribution allocation of 25% per team member.

## Repository

Public repository:

https://github.com/Yuvraj-Agarwal-101/CubeSat-Detumbling-with-Magnetorquers
