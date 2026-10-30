# Observed lecture-based revision checks

The latest shared baseline/report changes from origin/main at 86ff25f were merged into the local Person 4 branch. Existing user edits in PERSON4_HANDOFF.md were retained. Original course files remain outside the repository; docs/lecture_sources.json records their identifiers and hashes.

## Completed

- Full combined test suite passed 199 cases on Python 3.13.14 with NumPy 2.3.2, Matplotlib 3.10.5 and pytest 8.4.2. This includes upstream quaternion, dynamics and configuration checks plus Person 4 checks.
- `python run_all.py --demo --output data/processed/synthetic_lecture_revision` completed tests, analytic metric verification, 18 orbital fixtures, 36 paired fixtures, saved histories, summaries, monochrome PDF/PNG figures and manifests. No invalid fixture records occurred. Measured sweep-only runtimes were approximately 0.40 s and 0.72 s. These are fixture runtimes, not physics estimates.
- `python -m studies.metric_refinement --output data/processed/lecture_metric_check` produced six analytic sampling resolutions, exact values, errors, and a visually inspected monochrome figure.
- The state error diagnostic was checked using a manufactured h^4 output perturbation. Observed difference order is four for those prescribed outputs. This tests the diagnostic arithmetic, not an integrator implementation.
- RK4 modal checks were tested against known scalar amplification, the negative-real stability boundary near 2.785, eigenvalues -2 and -2000, neutral modes and growing modes. No spacecraft Jacobian spectrum is claimed.
- Case generation now validates every complete swept document using src.config, records override provenance, and derives the horizon from the canonical baseline. The 108 and 1152 case counts, deterministic ensembles and paired initial geometries remain checked.

## Local test environment

The Windows sandbox prevented pytest from creating its normal chmod-restricted temporary directory. A local-only pytest plugin supplied an ordinary workspace temporary path for the upstream tmp_path test. It was loaded through PYTEST_PLUGINS and is not part of the delivered repository. Test dependencies were unpacked locally because pip temporary paths were also restricted. No upstream test was changed for this workaround.

## Pending

The real physics adapter, field/control, scratch RK4, independent full-physics verification, smooth RK4 order study, saturation-aware step study and accepted production step remain pending. No real pilot or production study was run. Engineering performance and eventual recovery boundaries remain unknown. The updated LaTeX fragments are source deliverables and have not been compiled in this environment. Final clean clone reproduction, tested clean commit and publication remain pending.

AI assisted source reading, implementation revision, analytic verification, tests and report drafting. Team members must review the equations, code and interpretation. Contribution percentages remain for the team to record from actual work.
