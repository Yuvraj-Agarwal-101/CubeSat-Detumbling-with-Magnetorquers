# Team branch integration

## Subsequent Stage 3 numerical acceptance

[STAGE3_VERIFICATION.md](STAGE3_VERIFICATION.md) records regenerated merged-source
evidence and the pilot-only gate on `codex/production-step-gate`. The common
accepted step is 0.25 s after adding a real high-spin verification case: the
historical 1 s step passes the canonical cases but not the broader required
two-successive-refinement gate. Coarse failures, all finer comparisons, separate
output audits, and the canonical actuator stage-bound check are retained.
No real 108-case pilot or production engineering sweep was run.

## Subsequent Person 3 review

Sidhant's merged-source field/control review is recorded in
[PERSON3_REVIEW.md](PERSON3_REVIEW.md). The independent production callback and
RK4 stage checks pass, with 305 complete-suite tests passing. No production
field/controller correction was needed. The historical 1 s acceptance still
requires fresh merged-source timestep and output-grid evidence before the
108-case pilot. The integration execution record below retains its original scope.

## Scope and branch ancestry

Integration branch is `codex/merge-team-branches`, based on parent
`sidhant-final-integration` at `07fb961`. Main is unchanged and nothing was pushed.
`git fetch --all --prune` fetched all configured remotes. All five remote branches
were inspected through branch tips, unique logs, tree lists and change summaries.

`YUVRAJ_HANDOFF.md` does not exist in the checkout or fetched branch trees.
Yuvraj's complete available specification, `docs/person2_handoff.md`, was read
before merging; `docs/numerical_design.md` and numerical API contracts were retained.

Merges in order

1. `origin/yuvraj` at `9128b60`, two unique numerical architecture commits.
2. `origin/aleksandar` at `7f0a3de`, four unique physics and verification commits.
3. `origin/dibyansh` at `7ec6cce`, four unique experiment and lecture alignment commits.

`origin/workchunk_1_premise` at `bd2a95c` is already an ancestor of the starting
branch. It was not merged again. `origin/main` is the starting `07fb961`.

## Conflict resolutions

Yuvraj merged without conflicts. Aleksandar conflicted in these files.

| Files | Resolution |
| --- | --- |
| README.md | Preserve architecture and both numerical APIs, add real physics and current status, combine Person 4 commands later. |
| SHA256SUMS.txt | Regenerate final integrated snapshot after staging all files. Original checksum records are archived. |
| data/processed/convergence.csv, convergence.json | Retain Yuvraj's data paired with active PNG and terminal error fragment. Archive Aleksandar's overlapping measurements. |
| data/processed/run_summary.json, test_results.txt | Keep historical numerical records; fresh integration validation is separate. Both source versions are archived. |
| docs/dynamics_interface.md, docs/person2_interface.md | Keep reorganized paths and both APIs; append implemented callbacks, historical step scope and pending merged-source verification. |
| docs/submission_readiness.md | Keep numerical verification details; add integrated infrastructure and explicit remaining work. |
| report/PERSON2_FRAGMENTS.md | Regenerate from composed active sections, including separate terminal-error and time-weighted-error contributions. Original fragments are archived. |
| report/sections/method.tex | Keep Yuvraj's derivation and architecture, append Aleksandar's lecture stability interpretation, scales and limitations. Remove obsolete unavailable-model claim. |
| report/sections/numerical_verification.tex | Keep Yuvraj's distinct time-weighted study. Terminal errors stay in person2_verification.tex. |
| report/sections/verification.tex | Include both numerical contributions and all lecture, physics, full model and production step subsections. |
| report/sections/acknowledgments.tex, conclusions.tex, contributions.tex | Keep team review and pending engineering limitations, update implementation availability, preserve original drafts. |
| report/sections/reproducibility.tex | Combine numerical workflows and historical evidence scope; subsequently compose Person 4 workflow. |
| src/integrators.py | Preserve time-first wrapper delegating to scratch state-first RK4. Existing numerical layer rejects complex derivatives for real states; Aleksandar's validation tests pass. No second stage implementation replaces it. |
| run_all.py | Compose numerical drivers, preserve optional expensive verification, retain existing evidence on default runs. |
| studies/report_fragments.py | Keep independent terminal-error output path and local PNG; add physics/full-model sections and accurate implementation status. |

Dibyansh conflicted in these files.

| Files | Resolution |
| --- | --- |
| README.md | Compose numerical/physics and Person 4 commands; correct old claims that implemented modules are missing. |
| report/sections/reproducibility.tex | Retain both numerical and engineering reproduction instructions and evidence gates. |
| report/sections/results.tex | Retain Dibyansh's analytic metric evidence and pending engineering conclusions. Numerical physical evidence remains in the verification sections. |
| run_all.py | Dispatch explicit --demo or --verification workflows to studies/engineering_pipeline.py; keep numerical default, --adapter, --settings and --complete-verification. Reject conflicting workflow flags. |
| studies/__init__.py | Shared package description for both responsibilities. |
| studies/make_figures.py | Preserve run() for numerical convergence and generate(records, output) for engineering records. CLI supports no-argument convergence or paired --records/--output. |

Automatic merges retained canonical config compatibility, the separated physical,
solver and study structures, real callbacks, tests, bibliography entries, team_adapter,
metrics, experiment generation, sweep gates, refinement diagnostics and evidence.
report/main.tex includes experimental_method and both bibliographies. The artifact
manifest retains all numerical/physical entries and points to gated engineering
manifests without claiming generated engineering results.

## Historical evidence and test incompatibilities

The first system-Python test run used NumPy 1.x and failed five calls requiring
np.trapezoid. Installing the project's pinned direct dependencies in .venv fixes
this environment mismatch without changing the numerical formulas.

The other failure was substantive: Aleksandar's acceptance hashes identified
pre-reorganization dynamics and integrators. Hashes were not replaced with current
hashes to imply rerun evidence. Original conflicting records, drafts and exact
measured physics sources are under docs/integration_sources/{yuvraj,aleksandar}.
The active acceptance.json explicitly identifies the historical source revision
and snapshot root and states merged-source verification is pending. The evidence
test verifies original source hashes, unchanged live field/controller/adapter,
measured data hashes and the canonical baseline. It no longer confuses historical
acceptance with approval of the reorganized solver. Fresh timestep evidence will
also hash the reorganized implementation files, not just compatibility wrappers.
The original acceptance record is preserved in the source snapshots.

Two additional integration checks exercise both numerical APIs on the same short
real RHS and connect a Person 4 generated canonical case to the real adapter.
No six-orbit study, pilot or engineering sweep was started by this integration.
Existing test fixtures remain explicitly synthetic.

## Final validation

Windows Python 3.11, NumPy 2.0.2, Matplotlib 3.9.4 and pytest 8.4.2.
Complete available suite: **284 passed, zero failures**, using
`.venv/Scripts/python.exe -m pytest -q`.

Dependency check, canonical configuration validation, all active Python module
imports and compilation, runner and figure CLI help, report input/citation link
inspection, conflict-marker inspection and Git whitespace checks pass.
Integration pytest output is in docs/integration_validation/pytest.txt.
LaTeX compilation and final artifact rendering were not performed in this merge task.
Historical numerical logs retain their original environment and result counts.

Substantial changes are the src/physics, src/inputs and src/numerics architecture,
real orbit/controller and team_adapter modules, metric/experiment/diagnostic modules,
verification and engineering drivers, run_all.py, studies/make_figures.py, README,
report assembly and sections, manifests, evidence provenance and combined tests.

Ready for the next Person 3 verification task. Not approved for a new engineering
sweep: verify the merged numerical architecture against the historical physical
and timestep evidence, regenerate acceptance on the tested merged source, review
broader gains/geometries and output resolution, then prepare the Person 4 evidence
gate. Pilot and production runs, engineering conclusions, final contribution
percentages, student review, clean-clone final reproduction and submission remain
pending. Historical 1 s acceptance applies only to its recorded baseline scope.
