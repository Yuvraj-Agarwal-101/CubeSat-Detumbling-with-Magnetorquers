# Workchunk 4 record

Person 2 contributes generic classical RK4, an independent spherical torque free solution, a scalar nonautonomous exact case, six step convergence studies, monochrome figures, time step selection tooling and LaTeX method and verification sections.

All time advancement is implemented directly. Projection occurs only after completed steps and norm diagnostics are captured before correction. Both studies approach fourth order. Complete values, configuration, initial conditions, seeds and runtimes are in data/processed/convergence.json.

The combined suite has 147 passing tests. It retains the 124 existing quaternion and dynamics checks, adds 20 numerical and metric checks, and adds three integrations using actual shared dynamics with explicitly artificial zero torque control. Those integrations verify exact spherical rotation, four stage callback evaluation, and improving energy and inertial momentum conservation under refinement for asymmetric inertia. They do not verify the production magnetic controller.

The production field and controller and final configuration are unavailable. Full model unsaturated and saturated studies, production step selection and engineering sweeps remain pending. The refinement driver now uses a separate serializable config_record because the shared runtime config includes callbacks. Diagnostics use the shared controller output names.

The contribution uses the repository's existing direct dependencies. The complete fresh Python 3.12 Windows environment is recorded in requirements-python312.lock. The earlier Python 3.9 macOS lock is preserved. The README gives exact reproduction commands and manifest.json maps the numerical table and figure to their inputs and scripts.

AI assisted with extracting the handoff, implementing and reviewing the numerical code, running checks, adapting the code to the existing repository, generating figures, and preparing the report. Students must review, understand and independently verify this work. No student contribution percentages are invented. LaTeX compilation and the final teammate clean clone check remain pending.
