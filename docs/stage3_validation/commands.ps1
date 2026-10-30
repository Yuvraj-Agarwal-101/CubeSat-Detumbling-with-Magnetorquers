# Run at repository root with the existing pinned .venv environment.
# These regenerate numerical evidence only. No pilot or production command runs.
.venv/Scripts/python.exe -m pytest -q
.venv/Scripts/python.exe -m studies.physics_verification
.venv/Scripts/python.exe -m studies.verification
.venv/Scripts/python.exe -m studies.convergence
.venv/Scripts/python.exe -m studies.lecture_validation
.venv/Scripts/python.exe -m studies.metric_refinement --output data/processed/stage3_metric_verification
.venv/Scripts/python.exe -m src.config
.venv/Scripts/python.exe -m pip check
.venv/Scripts/python.exe -m compileall -q src studies docs/stage3_validation
rg -n 'solve_ivp|odeint|scipy\.integrate|from scipy' src studies team_adapter.py
# No matches are expected from the external-integrator source scan.
.venv/Scripts/python.exe -m studies.timestep_selection --adapter team_adapter --settings configs/full_model_refinement.json
.venv/Scripts/python.exe -m studies.complete_verification
.venv/Scripts/python.exe -m studies.refinement_audit --adapter team_adapter:simulate --rhs-adapter team_adapter:rhs_for_case --config configs/study.json --case-index 96 --step 1 --output data/processed/stage3_high_spin_audit
.venv/Scripts/python.exe docs/stage3_validation/stress_coarse.py
.venv/Scripts/python.exe -m studies.refinement_audit --adapter team_adapter:simulate --rhs-adapter team_adapter:rhs_for_case --config configs/study.json --case-index 96 --step 0.25 --output data/processed/stage3_high_spin_fine_audit
.venv/Scripts/python.exe docs/stage3_validation/extend_canonical.py
.venv/Scripts/python.exe docs/stage3_validation/merge_stress.py
.venv/Scripts/python.exe -m studies.baseline_confirmation --step 0.25
# The refinement audit refuses an existing directory; use a fresh path for reruns.
.venv/Scripts/python.exe -m studies.production_acceptance --apply
.venv/Scripts/python.exe -m studies.full_model_report
.venv/Scripts/python.exe -m studies.report_fragments
.venv/Scripts/python.exe -m pytest -q tests/test_gate_revision.py tests/test_output_resolution.py tests/test_person3_review.py
.venv/Scripts/python.exe -m pytest -q *> docs/stage3_validation/pytest_final.txt
.venv/Scripts/python.exe docs/stage3_validation/build_gate.py
git diff --check
# Commit the regenerated evidence before invoking this clean-checkout guard:
.venv/Scripts/python.exe -m studies.parameter_sweep --grid pilot --verification configs/verification.json --check-only
