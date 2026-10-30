# Shared project readiness

## Available

1. Engineering premise and complete stated initial value problem
2. Separate physics, case input, numerical algorithm, and study modules
3. Quaternion and Euler dynamics checks with backward compatible public imports
4. Shared SI case and generated parameter table
5. Explicit Euler, Heun, and RK4 implementations with stage evaluation and completed step projection
6. Weighted error norms, logarithmic order fits, local Jacobians, and amplification checks
7. Exact scalar and quaternion convergence studies
8. Asymmetric torque free conservation studies over finite trajectories
9. Three monochrome verification figures with saved data and an executable generator
10. Assembled report with method derivation and measured verification
11. Current test, revision, and environment records

## Pending

1. Production orbital field and controller callbacks and their interface acceptance
2. Saturation transition studies and local linear assessment along actual magnetic trajectories
3. A production time step justified by both accuracy and stability
4. Engineering metrics, sweep inputs and seeds, runtime estimates, detumbling figures, and interpretations
5. Final names, actual contribution records, percentages, and updated Acknowledgments
6. Full engineering runner and reproduction of all final results from a clean clone
7. Evaluator access and tested final revision checks after the remaining work is merged

## Current reproduction commands

Run from the repository root using the documented environment.

1. .venv/bin/python -m src.config
2. .venv/bin/python -m tools.check_project
3. .venv/bin/python -m studies.verification

The parameter table exporter is needed only after canonical inputs change. Saved verification figures describe numerical special cases rather than magnetic detumbling.

## Interpretation

Fourth order is supported for the tested smooth cases. It is not asserted across every saturation transition. A bounded linear amplification factor does not establish nonlinear stability or engineering accuracy. The production model has not yet been classified as nonstiff.

Integration status and historical-source scope are recorded in docs/INTEGRATION.md. The real field, controller, adapter and Person 4 pipeline are merged; engineering sweeps, renewed merged-source verification and final team review remain pending.
