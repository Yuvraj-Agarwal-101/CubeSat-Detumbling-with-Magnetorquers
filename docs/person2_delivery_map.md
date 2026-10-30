# Person 2 package integration map

All useful deliverables from the standalone Person 2 package were integrated into the shared repository layout.

1. src/integrators.py, tests, studies, configs, data/processed and figures retain their agreed locations. Existing src/__init__.py, quaternion.py and dynamics.py are preserved.
2. HANDOFF_EXTRACTED.md is docs/person2_handoff.md. source_extracted.txt is docs/person2_source_extracted.txt. Standalone interface guidance is updated in docs/person2_interface.md.
3. RESULTS.md is updated as report/WORKCHUNK_4.md. REPORT_FRAGMENTS.md is regenerated as report/PERSON2_FRAGMENTS.md.
4. The standalone README is merged into the existing team README. The existing .gitignore and references.bib are preserved. The original direct dependencies are reused rather than replaced. Plotting now uses the existing Matplotlib dependency. requirements-python312.lock records the tested environment.
5. LaTeX fragments remain in report/sections. The shared main.tex and verification.tex preserve team assembly. The generated numerical subsection is numerical_verification.tex. main_preview.tex remains an optional Person 2 preview. The acknowledgments draft is retained and the shared acknowledgments combines the recorded team contributions.
6. run_all.py runs the full team test suite before generating numerical results. manifest.json maps the delivered figure and table. Generated results and reproduction evidence are refreshed for the integrated version. SHA256SUMS.txt records final repository file checksums.

No notebooks, dependency environments, caches, credentials or redundant ZIP archive are added to Git. Full model scripts owned by other teammates are not replaced with synthetic production implementations.
