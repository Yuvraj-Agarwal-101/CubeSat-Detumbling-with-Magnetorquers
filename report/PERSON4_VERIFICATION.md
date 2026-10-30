# Person 4 observed verification

Base repository commit 79161bc. Local working branch person4-experiments. Checks run on Python 3.13.14 with NumPy 2.3.2, Matplotlib 3.10.5 and pytest 8.4.2.

- `python -m pytest -q -p no:cacheprovider` passed 78 cases including the 62 existing quaternion cases.
- `python run_all.py --demo --output data/processed/synthetic_checked` completed the tests, 18 orbital fixture cases and 36 paired fixture cases, saved histories, summaries, PDF/PNG plots and manifests.
- Fixture runner times were approximately 0.09 s and 0.17 s respectively, excluding tests and plotting. These times do not estimate the full physics cost.
- The generated time and success map was visually reviewed for legibility and explicit synthetic labels.
- Metric checks include analytically known crossing, complete hold at the deadline, excursions, equality, nonuniform time weighting, censoring, invalid histories, known effort and torque, and refined exponential threshold interpolation. These checks establish metric behavior on sampled interpolants, not accuracy of a spacecraft integrator.
- Pipeline checks confirm case counts of 108 and 1152, common geometries, deterministic seeds, paired configurations, missing-evidence rejection, history persistence and overwrite protection.

The Windows sandbox prevented normal pip temporary-directory operations. Test wheels were unpacked into an isolated workspace dependency directory and exposed through PYTHONPATH. This workaround is environment-specific and not part of the repository runtime. The listed direct versions were actually imported. No claim of a freshly installed lock or clean clone reproduction is made.

Pending dependencies are dynamics, orbit and field, controller, scratch RK4, independent full physics checks, convergence studies, accepted production step and output-grid refinement, real pilot, production, measured report conclusions, final publication and clean clone reproduction.

AI assisted code, tests, documentation, and pending LaTeX sections. No contribution percentages or numerical engineering findings have been invented.
