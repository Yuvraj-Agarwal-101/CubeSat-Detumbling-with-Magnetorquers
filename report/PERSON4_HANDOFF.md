# Person 4 integration contract

No other owner's physics or RK4 module is implemented here. Provide a small team_adapter.py after interfaces settle.

simulate(case, dt_s) -> dict` must return finite arrays `t (N,)`, `states (N,7)`, `raw_dipole (N,3)`, `dipole (N,3)`, `torque (N,3)`. Time begins at zero and ends exactly at `case['metrics']['deadline_s']`. All cases run the full horizon even after success. Evaluate forcing and control at every RK4 stage. Use only the team's scratch RK4. Retain quaternion norm diagnostics as an additional return array. The runner saves all returned arrays.

Case keys are demonstrated in configs/study.json and src/experiments.py. Translate these explicitly into the team's final configuration. Reject unsupported configurations rather than ignoring keys. `y0` is scalar first quaternion followed by body angular velocity in rad/s. `gain_kg_m2_s` is for normalized B dot. The dipole limit is a vector norm. `phase_rad` varies uniformly with the common geometry ensemble. `field_mode='frozen_inertial'` freezes the inertial field at initial phase and sets its inertial derivative to zero, but still rotates it to body coordinates. Person 1 must finalize assumptions and Person 3 must provide Earth dipole constants before real runs.

## Evidence gate

Copy configs/verification.example.json to a local verification record. Set booleans only after the actual checks pass. Person 2 supplies the accepted production step, name, tested commit, and evidence paths with SHA256 hashes. The independent physics checks, smooth RK4 convergence, saturation-aware step study, and threshold/hold output-grid refinement must be documented in those evidence files. This gate records team review; it cannot certify the truth of a manually entered claim. Real runs require a clean tracked checkout at the tested commit. The adapter must be committed before review.

Use `adapter: "team_adapter:simulate"`. Paths are relative to the repository root. `pilot_records` points to the measured 108-case real pilot JSONL on the same commit before production. The paired pilot has 216 cases and is separate. The proposed production grid has 1152 orbital cases. Runtime estimates are linear extrapolations from measured pilot time, not guarantees. Keep production grid provisional until the pilot is reviewed.

## Metrics

Threshold equality qualifies. Detumbling time is the earliest start of a complete 600 s interval with rate at or below 0.5 deg/s ending by the deadline. Crossings use linear interpolation of sampled angular rate norms. Hold detection includes all piecewise linear segments and resets after excursions. This interpolant cannot detect unresolved continuous excursions. Person 2 must refine output grids and integration steps around threshold crossings.

Saturation fraction integrates the above-limit duration of the piecewise linear raw dipole norm. Effort uses trapezoidal integration of commanded norm and is not electrical energy. Peak torque and final rate are output-sampled estimates. Missing recovery times stay JSON null. Valid deadline failures are censored; exceptions and nonfinite histories are invalid. Success fractions exclude invalid simulations with their count reported alongside the denominator. Final submission should resolve invalid simulations. Conditional median times are labeled as such, even when fewer than half succeed.

## Planned figure manifest

| Figure | Command | Configuration | Data |
| --- | --- | --- | --- |
| Time and success maps per gain | python -m studies.make_figures --records data/processed/production/records.jsonl --output figures/production | configs/study.json | production records and histories |
| Gain and saturation comparison | same command | configs/study.json | same common ensembles |
| Paired field comparison and outcomes | python -m studies.make_figures --records data/processed/production/paired.jsonl --output figures/paired | configs/paired.json | paired records and histories |

Generated manifest.json contains actual commands, config hashes, seeds, and source records. summary_table.json preserves counts, invalids, censoring, and conditional medians. paired_outcomes.json retains outcomes that cannot appear in the successful-pair scatter. Copy verified PDF figures to report/figures for Overleaf. Standard packages for the fragments are hyperref and graphicx. No fragment is inserted into another member's main.tex automatically.

AI assisted implementation, tests, documentation and draft pending report sections. Students must review and understand all changes. Actual contribution percentages and final AI acknowledgment remain the team's responsibility.


## Revision based on course lectures

The current generator obtains the physical dictionary and deadline from the canonical baseline. Each case contains document, a full validated src.config case with per-override provenance. The old flat physical keys described during initial development are superseded by the canonical physical.orbit, physical.magnetic and physical.controller structure. See docs/lecture_basis.md for lecture mapping, studies/refinement_audit.py for preproduction diagnostic checks and the README for commands. The user's existing handoff edit has been retained.
