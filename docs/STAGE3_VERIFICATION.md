# Stage 3 production numerical acceptance

Executed on `codex/production-step-gate`, parent integration branch `sidhant-final-integration`.
No push, 108-case pilot, production sweep, or engineering-result generation was performed.

Tested source commit: `e62bf63a2d1232047b6ca9d366f990d90d3dfb21`. Accepted production integration and output spacing: **0.25 s**.
The gate records the exact tested source commit and every tracked simulation/configuration/test blob. A later evidence-only commit is accepted only when that complete tree is identical. This avoids a gate having to contain its own enclosing commit hash; the clean tracked checkout and evidence SHA256 checks remain mandatory.

Automated numerical acceptance was executed by Codex at the user request. Student signoff, hardware validation, and blanket numerical approval of the full engineering grid are not claimed.

## Regenerated checks

The initial complete suite passed 305 tests. Final complete suite: 311 passed in 4.16s.
Smooth fitted RK4 orders: scalar 4.0540021665; spherical rotation 3.9994608948.
Independent field derivatives, static-field energy identities in both regimes, full RHS assembly, quaternion conventions, fresh RK4 stages, and projection diagnostics were rerun. Only the repository scratch RK4 is used; no external ODE integrator is used. Analytic metric verification was regenerated separately from spacecraft trajectories.

## Real full-model refinement

Every trajectory runs six orbital periods. Canonical cases have gain 1e-5 with limits 1 and 0.01 A m^2. The additional real stress case is seeded pilot geometry 0, 30 deg/s, gain 3e-5, limit 0.03 A m^2. Canonical integration comparisons retain endpoint hold/Boolean saturation screening metrics; stress comparisons use Person 4 interpolated metrics consistently at every level.

| Case | Step s | Success | Detumble start s | Final rate rad/s | Saturation fraction | Peak torque Nm | Max preprojection norm defect |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: |
| unsaturated | 2 | True | 16138.00000000 | 0.00216517360689 | 0 | 1.81230516857e-06 | 1.87744e-06 |
| unsaturated | 1 | True | 16135.00000000 | 0.00216539985781 | 0 | 1.81232695922e-06 | 5.34146e-08 |
| unsaturated | 0.5 | True | 16135.00000000 | 0.00216541095209 | 0 | 1.81378101182e-06 | 1.59195e-09 |
| unsaturated | 0.25 | True | 16135.00000000 | 0.00216541102712 | 0 | 1.81378104563e-06 | 5.06599e-11 |
| unsaturated | 0.125 | True | 16134.87500000 | 0.00216541101218 | 0 | 1.81382967558e-06 | 1.60183e-12 |
| unsaturated | 0.0625 | True | 16134.87500000 | 0.00216541101063 | 0 | 1.81383878152e-06 | 5.04041e-14 |
| saturated | 2 | True | 24596.00000000 | 0.00263776259069 | 0.3675806162 | 4.38572261074e-07 | 2.03113e-06 |
| saturated | 1 | True | 24568.00000000 | 0.00271695102411 | 0.3675953183 | 4.38572261074e-07 | 5.70032e-08 |
| saturated | 0.5 | True | 24567.00000000 | 0.00271853026842 | 0.3676467754 | 4.38572261074e-07 | 1.70212e-09 |
| saturated | 0.25 | True | 24566.75000000 | 0.00271854631167 | 0.3676063448 | 4.38572261074e-07 | 5.1988e-11 |
| saturated | 0.125 | True | 24566.75000000 | 0.00271855297948 | 0.367589805 | 4.38572261074e-07 | 1.60583e-12 |
| saturated | 0.0625 | True | 24566.75000000 | 0.00271855202021 | 0.3675999127 | 4.38572261074e-07 | 5.00711e-14 |
| high_spin | 2 | True | 19093.62951757 | 0.0021645987949 | 0.42066209 | 1.3288878771e-06 | 0.000693766 |
| high_spin | 1 | True | 20539.93301364 | 0.00227277044339 | 0.4825276793 | 1.33683580073e-06 | 1.67055e-05 |
| high_spin | 0.5 | True | 20651.85476325 | 0.00229499850181 | 0.4857688275 | 1.33683580073e-06 | 4.4192e-07 |
| high_spin | 0.25 | True | 20622.34363336 | 0.00226229303542 | 0.4843053485 | 1.33683581362e-06 | 1.27938e-08 |
| high_spin | 0.125 | True | 20621.47469638 | 0.00225651197625 | 0.4842398946 | 1.33683581608e-06 | 3.84896e-10 |
| high_spin | 0.0625 | True | 20621.43561715 | 0.00225620862045 | 0.4842361759 | 1.33683581708e-06 | 1.18152e-11 |

One percent relative tolerance applies to detumbling time, final rate and peak torque, with absolute floors 1 s, 1e-6 rad/s, and 1e-10 Nm; saturation fraction tolerance is absolute 0.005. Two consecutive comparisons and unchanged success classification must pass for every case. All failed/coarse comparisons remain in timestep_selection.json.

| Case | Refinement s | Pass | Time change s | Rate change rad/s | Saturation change | Peak torque change Nm |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| unsaturated | 2 to 1 | True | 3 | 2.2625092e-07 | 0 | 2.1790655e-11 |
| unsaturated | 1 to 0.5 | True | 0 | 1.1094281e-08 | 0 | 1.4540526e-09 |
| unsaturated | 0.5 to 0.25 | True | 0 | 7.5030532e-11 | 0 | 3.3804428e-14 |
| unsaturated | 0.25 to 0.125 | True | 0.125 | 1.4942402e-11 | 0 | 4.8629953e-11 |
| unsaturated | 0.125 to 0.0625 | True | 0 | 1.5471548e-12 | 0 | 9.1059455e-12 |
| saturated | 2 to 1 | False | 28 | 7.9188433e-05 | 1.4702048e-05 | 4.1292856e-21 |
| saturated | 1 to 0.5 | True | 1 | 1.5792443e-06 | 5.145717e-05 | 2.646978e-22 |
| saturated | 0.5 to 0.25 | True | 0.25 | 1.6043251e-08 | 4.0430633e-05 | 5.2939559e-23 |
| saturated | 0.25 to 0.125 | True | 0 | 6.6678156e-09 | 1.6539805e-05 | 1.0587912e-22 |
| saturated | 0.125 to 0.0625 | True | 0 | 9.5926953e-10 | 1.0107658e-05 | 1.0587912e-22 |
| high_spin | 2 to 1 | False | 1446.3035 | 0.00010817165 | 0.061865589 | 7.9479236e-09 |
| high_spin | 1 to 0.5 | True | 111.92175 | 2.2228058e-05 | 0.0032411482 | 2.5114527e-19 |
| high_spin | 0.5 to 0.25 | False | 29.51113 | 3.2705466e-05 | 0.001463479 | 1.2886792e-14 |
| high_spin | 0.25 to 0.125 | True | 0.86893697 | 5.7810592e-06 | 6.5453934e-05 | 2.4642571e-15 |
| high_spin | 0.125 to 0.0625 | True | 0.039079233 | 3.033558e-07 | 3.7186754e-06 | 9.9478916e-16 |

The historical 1 s step passes the renewed canonical checks but fails the broader two-successive-refinement requirement: the high-spin 0.5 to 0.25 s final-rate comparison exceeds 1%. This measured failure is why the pilot step was reduced.

## Separate output/event audit

Hold each finest trajectory fixed and coarsen only its output. Threshold equality qualifies; full uninterrupted 600 s hold intervals are required. Piecewise linear rate-norm crossings and raw-dipole-norm saturation crossings are checked independently against the actual Person 4 metrics. Peak torque remains a sampled maximum. Refinement supports resolution for these measured histories; it does not prove that no subgrid excursion exists.

| Case | Output spacing s | Hold start s | Saturation fraction | Peak torque Nm |
| --- | ---: | ---: | ---: | ---: |
| unsaturated | 0.25 | 16134.853363816 | 0 | 1.81378104749e-06 |
| unsaturated | 0.125 | 16134.853342592 | 0 | 1.8138296757e-06 |
| unsaturated | 0.0625 | 16134.853340371 | 0 | 1.81383878152e-06 |
| saturated | 0.25 | 24566.688689174 | 0.3675906278 | 4.38572261074e-07 |
| saturated | 0.125 | 24566.688670962 | 0.3675905738 | 4.38572261074e-07 |
| saturated | 0.0625 | 24566.688661850 | 0.3675905286 | 4.38572261074e-07 |
| high_spin | 0.25 | 20621.435665787 | 0.4842485709 | 1.33683581362e-06 |
| high_spin | 0.125 | 20621.435632729 | 0.484238204 | 1.33683581608e-06 |
| high_spin | 0.0625 | 20621.435617148 | 0.4842361759 | 1.33683581708e-06 |

All output comparisons pass; largest adjacent hold-start change is 3.30581643e-05 s (required <=1 s). Success classification is unchanged.
Quarter/eighth/sixteenth canonical audit JSONs are retained. Full stress histories and final compact scalar traces permit output-audit reproduction.

## Canonical actuator bound

At 0.25 s, the canonical 0.1 A m^2 actuator **does not saturate** at any of 544144 evaluated RK4 stages. The maximum raw dipole norm is 0.0702340425898 A m^2. Maximum preprojection/projected quaternion norm defects are 5.06599e-11 / 3.33067e-16. Metrics agree with the unsaturated reference to the recorded roundoff tolerance. This result applies only to the canonical baseline, not every future sweep case.

## Reproduction and next action

Exact numerical commands are in `docs/stage3_validation/commands.ps1`; terminal logs are alongside it. The first premature baseline attempt correctly refused an unselected step; its log is retained as baseline_prerequisite.txt. The refinement directories refuse overwrites; use fresh paths for reruns.

Gate: `configs/verification.json`. Run the zero-simulation check after committing evidence:
```powershell
.venv/Scripts/python.exe -m studies.parameter_sweep --grid pilot --verification configs/verification.json --check-only
```

NEXT, after this task (not executed here):
```powershell
.venv/Scripts/python.exe -m studies.parameter_sweep --config configs/study.json --grid pilot --verification configs/verification.json --output data/processed/pilot/records.jsonl
```

Expected pilot output: `data/processed/pilot/records.jsonl`, `records.summary.json`, and `records_histories/`. The real 108-case pilot and its runtime/accuracy review remain mandatory before the 1152-case production grid. No pilot_records field is fabricated. Production remains blocked until real valid pilot records on the production tested commit exist.

## Evidence SHA256 (raw file bytes)

| Path | SHA256 |
| --- | --- |
| `data/processed/physics_verification.json` | `e9529b7d9519f9f576df9fd091ffe2e03eeda85627f69c36b42fa5de1174a075` |
| `data/processed/verification_summary.json` | `cda40735dadbbb5a1663afca0719b118bc0ad7b0c0c30ef353272e7ecbb09676` |
| `data/processed/convergence.json` | `93263f82dd3a43e01451ea5a1802fda556fed6517110ea65b883d747ed547890` |
| `data/processed/lecture_validation.json` | `551adcdf6c4c7b750d65dbc58e367728cd76526e7ba1e5f419f91c081589b615` |
| `data/processed/stage3_metric_verification/evidence.json` | `feff430190538e0e63adc95bb8e345e4b287dd15094c524a43f43dd5efa77f4b` |
| `data/processed/timestep_selection.json` | `2375119e91589903926f9e6843ced665690e487cf8aaeb92fd6c9307184d195d` |
| `data/processed/production_validation/acceptance.json` | `f62cfc765ab7855281e80d233c45f9ec5f431d744333f97a5faf6c4605af4f6b` |
| `data/processed/production_validation/confirmation.json` | `caad466546e00caf3d1d9d7c9b9aef5feba7f9e9c5e1870760537fb74f406754` |
| `data/processed/production_validation/baseline.json` | `349263124545620d854362bc11b08d3177d75ccfc099a1b1cbf16514243e24cc` |
| `data/processed/production_validation/unsaturated_trace.npz` | `17ddcb7c04cabb5090446f96cbbd66dafb218cbe99e0467236565e09f63c8f31` |
| `data/processed/production_validation/saturated_trace.npz` | `855e998eff43f3b3e28fc7152f0fd7875ff9c0c3aab361411a9a977a2ca72662` |
| `data/processed/stage3_high_spin_audit/audit.json` | `cd5ccd507bf9c81579e22eafd5b53fac2573406279f601dd6667ab6c5f8f4c9d` |
| `data/processed/stage3_high_spin_audit/coarse_2s.json` | `90f68d9afe52899bda4db0b275e3caf2890bbfe6ef1c164045b0ad9e71fdfdd4` |
| `data/processed/stage3_high_spin_fine_audit/audit.json` | `c8ed4ec08dac432b9336527c11f020a23d1376e3e55d222265d8db3ada26ae1c` |
| `data/processed/production_validation/high_spin_trace.npz` | `2ba743997cef8342c35bc25ca60ac3d4441c886da97b5d41090f0323f083f516` |
| `docs/stage3_validation/pytest_initial.txt` | `5b8777bcee0161c480b8a713d750d254d0b65a4da72b95282676072f438aeb25` |
| `docs/stage3_validation/pytest_final.txt` | `bbff441f8404047eacae818fe4a6f6cdbea8b82375f2f7d42d9514a39b3e4aa0` |
| `docs/stage3_validation/targeted.txt` | `1689b9a0639b6c737d8056b5fe67634ce074d96b553c7205c74abbd46aede4bf` |
| `docs/stage3_validation/summary.json` | `a8800398fc59ce77720ed47e74496c3351fd5d931dcdf2b0050044a49e6afa02` |
| `docs/stage3_validation/environment.json` | `ea4f920339d293da5ecf7eb9f264317d9a5f1a8a86500b9402072effc79557c1` |
| `docs/stage3_validation/build_gate.py` | `9170947a37a59494888b58b7a20aafa796e46af9570c876494df8f01fab97188` |
| `docs/stage3_validation/commands.ps1` | `05d866cc1610b051bf6f1385ac529cd169d71ed0b6cdb5206b564b5621a56871` |
| `docs/stage3_validation/extend_canonical.py` | `95033794862111b99d576645818f7298abce4e3d804ef659d12e351b187a707c` |
| `docs/stage3_validation/merge_stress.py` | `77fcbfd5e19c0422fd238d9588bfe450208f91288b4112cadab46139c96fd3da` |
| `docs/stage3_validation/stress_coarse.py` | `64f81b67bb4fe2d68b070cf6f44d6fb4670ca6b2a7b35e68d3e1b8d663626467` |
| `data/processed/stage3_high_spin_audit/coarse_2s.npz` | `ab7a15fa2c49aaa441422d97f296626e6544db80338cb4f434436b2ef7c31dfa` |
| `data/processed/stage3_high_spin_audit/level_0.npz` | `3a4a3257a1fff8ee9b8aa205afa8f96e999130eb469d0c56763e5734ed8d0270` |
| `data/processed/stage3_high_spin_audit/level_1.npz` | `9ab147063f735eb0f5e45f8f732dd90ec5117a6329dfde2ec83de1b2ab20ae1a` |
| `data/processed/stage3_high_spin_audit/level_2.npz` | `8001fd691e915a26f63d2566f00330878692f9dd3b6104388c2e81e82b97ca69` |
| `data/processed/stage3_high_spin_fine_audit/level_0.npz` | `8001fd691e915a26f63d2566f00330878692f9dd3b6104388c2e81e82b97ca69` |
| `data/processed/stage3_high_spin_fine_audit/level_1.npz` | `3d7ca4e7212eaaf91f96ffcc47d0e57a29027d4f24243bcc810b49cf2d1f38c8` |
| `data/processed/stage3_high_spin_fine_audit/level_2.npz` | `5a500bae385dfbd6eb486eef23944ab9c7de308e18b8d176eb229f322a3aa46f` |
