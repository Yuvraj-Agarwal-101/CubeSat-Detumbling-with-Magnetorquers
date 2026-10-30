# Remaining Person 1 work records

## Workchunk 4

Added configs/baseline.json and src/config.py. Physical inputs, initial conditions, study criteria, solver settings, and provenance are separate. Initial values are SI. Validation covers structure, finite values, positive definite inertia, a unit quaternion, positive actuator and controller bounds, angular ranges, valid durations, and metadata coverage.

The production step is unset until convergence and metric refinement justify it. runtime_config binds explicit field and controller callbacks without mixing solver or study settings into the physics. A labeled fixture test verifies compatibility with the existing dynamics. All 50 configuration cases pass.

The report parameter table is generated from the baseline and has an independent consistency check. There are 175 passing cases across the current repository.

## Workchunk 5

Recorded orbit and field constants, frames, phases, rotation conventions, the total derivative along the orbit, body rotation correction, normalized gain units, vector norm saturation, and acceptance checks in docs/field_controller_contract.md. Extended the report with matching convention text and the runtime configuration contract.

Person 3's production modules are absent. This is completed technical preparation and an executable callback boundary, not a claim of teammate agreement or production integration. Acceptance against those modules remains an external dependency.

## Workchunk 6

Assembled the report using separate premise, method, verification, results, conclusions, contributions, reproducibility, and Acknowledgments files. Existing verification fragments are placed in the shared verification section. The current report identifies pending work rather than inventing numerical evidence or final contribution percentages.

Added tools/check_project.py to record current tests, baseline summary, Python version, full Git revision, and working tree status. Added tools/export_report_inputs.py to generate the canonical table. These commands are available checks and do not replace Person 4's future full simulation runner.

Added the submission readiness record in docs/submission_readiness.md. Final contribution percentages, teammate acceptance, numerical convergence evidence, production results, and clean clone reproduction remain pending.

## AI use

AI assisted with the configuration implementation and validation, table generation, test design, interface specifications, report assembly, and reproduction records. The Acknowledgments draft records the work actually performed in this project contribution.
