# Real gate validation after committing evidence

Executed at evidence commit `96e848f260966abe0ef12a304da2a31967cbb129`,
with tested source commit `e62bf63a2d1232047b6ca9d366f990d90d3dfb21`.
The complete source/configuration tree is identical between them.

```powershell
.venv/Scripts/python.exe -m studies.parameter_sweep --config configs/study.json --grid pilot --verification configs/verification.json --check-only
.venv/Scripts/python.exe -m studies.parameter_sweep --config configs/study.json --grid production --verification configs/verification.json --check-only
.venv/Scripts/python.exe -m pytest -q
git diff --check
```

The pilot check resolves `team_adapter:simulate` with `dt_s = 0.25`, counts
108 planned cases, and reports `simulations_run = 0`. See `backend_check.txt`.
The negative production check raises `ValueError: Production requires pilot_records`,
as required; see `production_block_check.txt`. Neither command creates study results.
The final complete suite passes **311 tests** in 4.15 s; see `pytest_gate_final.txt`.
Whitespace verification passes.

The pilot records and histories paths remain absent. The only remaining entry
action is the real 108-case pilot documented in `../STAGE3_VERIFICATION.md`.
Its runtime and accuracy review must precede production approval.
