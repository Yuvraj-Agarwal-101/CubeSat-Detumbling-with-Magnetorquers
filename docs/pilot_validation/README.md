# Final targeted engineering study — October 30, 2026

The deadline change replaced the planned 108-case pilot with a **16-case targeted engineering study**. There are **15 successes, 1 censored deadline failure, and 0 invalid completed simulations**. No more engineering simulations are authorized. The 108-case pilot and 1152-case production sweep were not completed. **PRODUCTION SWEEP READY: NO**; the original pilot requirement remains unmet by design. This is not a failure of the accepted timestep.

## Measured evidence

- Tested engineering source commit: `56f7d04a57ef5c26d60b3ee796626ae1bb43f4e1`, branch `codex/real-108-pilot`.
- Adapter: `team_adapter:simulate`; real idealized orbital field, normalized B-dot feedback, vector-norm clipping, scratch RK4.
- Step: 0.25 s from the real verification gate; final shortened step ends at 34008.86621436699 s (six orbits).
- Success: angular-rate norm <= 0.5 deg/s for a full 600 s hold ending by the deadline. Censored times remain null.
- Seed: 3702026. All cases retain the complete 136037-sample history.
- Final records: `data/processed/targeted/records.jsonl`; validation, summary, CSV table, and SHA256 manifest in the same directory. Histories are in the record-specific `pilot/shards` and `targeted/shards` paths.
- Figure manifest: `figures/targeted/manifest.json`; report copies in `report/figures`.
- Stage 3 source, configurations, verification evidence, and accepted step are unchanged.

## Exact execution and interrupted attempts

1. The requested serial command was started using global Python, then interrupted without any completed case after discovering incompatible global NumPy. The isolated empty output is `data/processed/pilot_interrupted_global_python`.
2. The same command with `.venv/Scripts/python.exe` was started and interrupted without a completed case when changing to process-level parallel execution. The empty output is `data/processed/pilot_interrupted_serial`.
3. The real unchanged gated runner was called once per case by:

   `.venv/Scripts/python.exe docs/pilot_validation/run_parallel_pilot.py --workers 12 --output data/processed/pilot/records.jsonl`

   At that time the wrapper queued the original 108-case design. Twelve cases completed in 408.2635 s wall time (401.8434–407.3227 s per case). When the deadline instruction arrived, the next twelve queued cases had already started. The process tree was stopped immediately; indices 12–23 have empty interrupted records and no completed histories. These interrupted tasks are not silently omitted numerical failures and are not included in the completed 16-case study. The retained `pilot/progress.jsonl` documents the 12 completions. There is deliberately no completed 108-case aggregate.
4. The final and only additional batch was:

   `.venv/Scripts/python.exe docs/pilot_validation/run_parallel_pilot.py --workers 4 --indices 72,24,96,104 --output data/processed/targeted/additional.jsonl`

   Four cases completed in 241.2077 s wall time (239.6451–240.5642 s each), with 3 successes and 1 censored failure. No further simulations followed. The wrapper now defaults to the final targeted design and refuses more than 24 cases.

## Final design and interpretation

The first twelve are all combinations of spin 1 deg/s, gain 3e-6 kg m²/s, limits 0.03/0.1/0.3 A m², and geometry IDs 0/1/2/3. The four additions, all at geometry 0, are `(spin, gain, limit)` = `(30,3e-6,0.03)`, `(1,3e-5,0.03)`, `(30,3e-5,0.03)`, `(30,3e-5,0.3)`. Full initial quaternions, spin directions, and phases are in the records.

Successful recovery times span 862.9406–20622.3436 s, with conditional median 8043.2288 s. Saturation fractions span 0–0.48430535; sampled peak torques span 4.28439e-8–8.57280e-6 N m. The single failure is `(30,3e-6,0.03,geometry 0)`, ending at 4.4130 deg/s. Increasing gain tenfold reduces the matched low-spin time by 90.91% and changes the high-spin failure to success. Increasing the high-spin/high-gain actuator limit tenfold reduces time by 61.00% and saturation from 48.43% to 1.56%. At low spin/low gain, all limits are inactive and trajectories agree exactly across limits. Four joint geometries vary recovery time by a factor 3.89. These are tested-case observations, not population statistics or a global optimum.

## No-simulation deliverable commands

```powershell
.venv/Scripts/python.exe docs/pilot_validation/build_submission.py
.venv/Scripts/python.exe -m pytest -q
.venv/Scripts/python.exe docs/pilot_validation/check_report.py
```

The first command independently validates all intended cases and histories, recomputes every metric, and creates the final three figures, case table, summary, and manifest. The final command checks included files, figures, citation keys, labels, stale claims, and creates `report/Overleaf_submission.zip`. It does not claim LaTeX layout validation. No local `pdflatex`, `latexmk`, `xelatex`, `lualatex`, or `tectonic` is available (see `environment.json`). Upload the ZIP to Overleaf and compile `main.tex`.

Only remaining report input TODO: team-agreed contribution percentages. Names and repository-supported responsibilities are populated; no percentages are invented. The supplied student-team review statement is included in the AI acknowledgment.

The independent-reproduction simulation command is in the report. It is documentation for a future reviewer, **not** permission to run further cases during this submission task.
