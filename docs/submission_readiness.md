# Shared project readiness

## Available

1. Engineering premise and full initial value problem
2. Quaternion utilities and 62 passing geometry cases
3. Euler dynamics and 62 passing instantaneous cases
4. Shared SI configuration and 50 passing configuration cases
5. Canonical report parameter table and its consistency test
6. Explicit orbit field and control connection contract
7. Assembled Overleaf report with accurate draft status
8. Current checks with generated revision and environment evidence
9. Generic RK4, exact solution convergence, numerical report text and monochrome figure
10. Shared dynamics integration tests and a production refinement driver awaiting real callbacks

## Pending by owner

1. Person 1 and Person 3 must confirm the real field and controller interface after those modules are supplied.
2. Person 2 has supplied the integrator, derivation, error and stability discussion, independent exact solution comparison and convergence evidence. Real smooth and saturated metric refinement and a justified production step remain pending.
3. Person 3 must provide the production field, total derivative, normalized controller, saturation, and physics tests.
4. Person 4 must provide verified metrics, sweeps, seeds, runtime estimates, plots, the figure and table manifest, and the full reproduction pipeline.
5. All members must provide actual names, contribution records, final percentages, and updates to the AI usage account.
6. A teammate must reproduce all final results from a clean clone and verify evaluator access and the tested final commit.

## Current commands

Run these from the repository root after creating the documented environment.

1. .venv/bin/python -m src.config
2. .venv/bin/python -m tools.check_project
3. .venv/bin/python -m tools.export_report_inputs
4. .venv/bin/python run_all.py

The third command is needed only after changing the canonical baseline. The report consistency test prevents a stale parameter table.

## Report sections

The report follows the assignment categories. The numerical method and exact solution evidence are now included. Engineering results remain explicitly pending. Quaternion, dynamics, and configuration checks are completed evidence. Field and control conventions are a specification rather than a completed production model.

The measured exact solution study establishes numerical convergence for its stated cases. It does not establish recovery performance, final contribution percentages, production step selection or complete final submission readiness.
