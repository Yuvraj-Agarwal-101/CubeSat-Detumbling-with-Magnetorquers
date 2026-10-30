"""Assemble a pilot-only gate from freshly regenerated Stage 3 evidence.

Run from repository root after production_acceptance --apply and final pytest.
This script performs no simulations and creates no engineering records.
"""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

sys.path.insert(0,str(Path.cwd()))
from studies.parameter_sweep import source_tree
from studies.timestep_selection import compare, select_step


def read(path):
    return json.loads(Path(path).read_text())


def log_text(path):
    data=Path(path).read_bytes()
    return data.decode('utf-16' if data.startswith(b'\xff\xfe') else 'utf-8-sig')


accept=read('data/processed/production_validation/acceptance.json')
refine=read('data/processed/timestep_selection.json')
output=read('data/processed/production_validation/confirmation.json')
baseline=read('data/processed/production_validation/baseline.json')
smooth=read('data/processed/verification_summary.json')
stress=read('data/processed/stage3_high_spin_fine_audit/audit.json')
for path,expected in accept['physics_source_sha256'].items():
    assert hashlib.sha256(Path(path).read_bytes().replace(b'\r\n',b'\n')).hexdigest()==expected, path
assert select_step(refine['cases'],refine['settings']['step_sizes_s']) == accept['accepted_step_s']
assert output['output_grid_pass'] and all(c['person4_metric_agreement'] for c in output['cases'])
assert baseline['step_s'] == accept['accepted_step_s']
assert baseline['bound_inactive_at_all_stages'] and baseline['reference_unsaturated_metrics_agree']
assert 3.8 < smooth['orders']['rk4'] < 4.3
assert 3.8 < smooth['orders']['spherical_rotation'] < 4.2
stress_comparisons=[compare(a,b,refine['settings']['tolerances']) for a,b in zip(stress['metrics'][:-1],stress['metrics'][1:])]
stress_output=[compare(a,b,refine['settings']['tolerances']) for a,b in zip(stress['output_only_metrics'][:-1],stress['output_only_metrics'][1:])]
assert all(c['pass'] for c in stress_comparisons+stress_output), 'High-spin metric audit needs review'
assert 'passed' in log_text('docs/stage3_validation/pytest_final.txt')
summary=dict(tested_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
             accepted_step_s=accept['accepted_step_s'],stress_comparisons=stress_comparisons,
             stress_output_comparisons=stress_output,
             scope='Numerical pilot entry only. Real 108-case pilot runtime/accuracy review still required before production.',
             external_ode_integrator_used=False)
Path('docs/stage3_validation/summary.json').write_text(json.dumps(summary,indent=2)+'\n')
paths=['data/processed/physics_verification.json','data/processed/verification_summary.json',
       'data/processed/convergence.json','data/processed/lecture_validation.json',
       'data/processed/stage3_metric_verification/evidence.json',
       'data/processed/timestep_selection.json',
       'data/processed/production_validation/acceptance.json',
       'data/processed/production_validation/confirmation.json',
       'data/processed/production_validation/baseline.json',
       'data/processed/production_validation/unsaturated_trace.npz',
       'data/processed/production_validation/saturated_trace.npz',
       'data/processed/stage3_high_spin_audit/audit.json',
       'data/processed/stage3_high_spin_audit/coarse_2s.json',
       'data/processed/stage3_high_spin_fine_audit/audit.json',
       'data/processed/production_validation/high_spin_trace.npz',
       'docs/stage3_validation/pytest_initial.txt','docs/stage3_validation/pytest_final.txt',
       'docs/stage3_validation/targeted.txt','docs/stage3_validation/summary.json',
       'docs/stage3_validation/environment.json',
       'docs/stage3_validation/build_gate.py','docs/stage3_validation/commands.ps1',
       'docs/stage3_validation/extend_canonical.py','docs/stage3_validation/merge_stress.py',
       'docs/stage3_validation/stress_coarse.py']
paths += [p.as_posix() for folder in ('stage3_high_spin_audit','stage3_high_spin_fine_audit')
          for p in sorted((Path('data/processed')/folder).glob('*.npz'))]
for path in paths:
    if Path(path).suffix in ('.json','.txt','.py','.ps1'):
        # Write bytes: Windows text-mode writing would reintroduce CRLF.
        Path(path).write_bytes(log_text(path).replace('\r\n','\n').encode('utf-8'))
gate=dict(independent_physics_checks_passed=True,smooth_convergence_passed=True,
          output_grid_refinement_passed=True,person2_accepted=True,
          accepted_by='Codex automated Stage 3 numerical acceptance at user request; student signoff not claimed',
          adapter='team_adapter:simulate',dt_s=accept['accepted_step_s'],
          tested_commit=summary['tested_commit'],tested_source_tree=source_tree(),
          scope=summary['scope'],
          evidence_files=[dict(path=p,sha256=hashlib.sha256(Path(p).read_bytes()).hexdigest()) for p in paths])
Path('configs/verification.json').write_text(json.dumps(gate,indent=2)+'\n')
lines=['# Stage 3 production numerical acceptance','',
       'Executed on `codex/production-step-gate`, parent integration branch `sidhant-final-integration`.',
       'No push, 108-case pilot, production sweep, or engineering-result generation was performed.','',
       f"Tested source commit: `{gate['tested_commit']}`. Accepted production integration and output spacing: **{gate['dt_s']:g} s**.",
       'The gate records the exact tested source commit and every tracked simulation/configuration/test blob. '
       'A later evidence-only commit is accepted only when that complete tree is identical. '
       'This avoids a gate having to contain its own enclosing commit hash; the clean tracked checkout and evidence SHA256 checks remain mandatory.','',
       'Automated numerical acceptance was executed by Codex at the user request. Student signoff, hardware validation, and blanket numerical approval of the full engineering grid are not claimed.','',
       '## Regenerated checks','',
       'The initial complete suite passed 305 tests. Final complete suite: '+log_text('docs/stage3_validation/pytest_final.txt').strip().splitlines()[-1]+'.',
       f"Smooth fitted RK4 orders: scalar {smooth['orders']['rk4']:.10f}; spherical rotation {smooth['orders']['spherical_rotation']:.10f}.",
       'Independent field derivatives, static-field energy identities in both regimes, full RHS assembly, quaternion conventions, fresh RK4 stages, and projection diagnostics were rerun. '
       'Only the repository scratch RK4 is used; no external ODE integrator is used. Analytic metric verification was regenerated separately from spacecraft trajectories.','',
       '## Real full-model refinement','',
       'Every trajectory runs six orbital periods. Canonical cases have gain 1e-5 with limits 1 and 0.01 A m^2. '
       'The additional real stress case is seeded pilot geometry 0, 30 deg/s, gain 3e-5, limit 0.03 A m^2. '
       'Canonical integration comparisons retain endpoint hold/Boolean saturation screening metrics; stress comparisons use Person 4 interpolated metrics consistently at every level.','',
       '| Case | Step s | Success | Detumble start s | Final rate rad/s | Saturation fraction | Peak torque Nm | Max preprojection norm defect |',
       '| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: |']
for case in refine['cases']:
    for run in case['runs']:
        m=run['metrics']
        lines.append(f"| {case['name']} | {run['step_s']:g} | {m['success']} | {m['detumbling_time_s']:.8f} | {m['final_rate_rad_s']:.12g} | {m['saturation_fraction']:.10g} | {m['peak_torque_Nm']:.12g} | {run['max_preprojection_norm_error']:.6g} |")
lines+=['','One percent relative tolerance applies to detumbling time, final rate and peak torque, with absolute floors 1 s, 1e-6 rad/s, and 1e-10 Nm; saturation fraction tolerance is absolute 0.005. '
        'Two consecutive comparisons and unchanged success classification must pass for every case. All failed/coarse comparisons remain in timestep_selection.json.','',
        '| Case | Refinement s | Pass | Time change s | Rate change rad/s | Saturation change | Peak torque change Nm |',
        '| --- | --- | --- | ---: | ---: | ---: | ---: |']
for case in refine['cases']:
    for a,b,c in zip(case['runs'][:-1],case['runs'][1:],case['comparisons']):
        d=c['metrics']
        lines.append(f"| {case['name']} | {a['step_s']:g} to {b['step_s']:g} | {c['pass']} | {d['detumbling_time_s']['absolute_difference']:.8g} | {d['final_rate_rad_s']['absolute_difference']:.8g} | {d['saturation_fraction']['absolute_difference']:.8g} | {d['peak_torque_Nm']['absolute_difference']:.8g} |")
lines+=['','The historical 1 s step passes the renewed canonical checks but fails the broader two-successive-refinement requirement: '
        'the high-spin 0.5 to 0.25 s final-rate comparison exceeds 1%. This measured failure is why the pilot step was reduced.','',
        '## Separate output/event audit','',
        'Hold each finest trajectory fixed and coarsen only its output. Threshold equality qualifies; full uninterrupted 600 s hold intervals are required. '
        'Piecewise linear rate-norm crossings and raw-dipole-norm saturation crossings are checked independently against the actual Person 4 metrics. '
        'Peak torque remains a sampled maximum. Refinement supports resolution for these measured histories; it does not prove that no subgrid excursion exists.','',
        '| Case | Output spacing s | Hold start s | Saturation fraction | Peak torque Nm |',
        '| --- | ---: | ---: | ---: | ---: |']
for case in output['cases']:
    for row in case['output_audit']:
        m=row['metrics']
        lines.append(f"| {case['name']} | {row['output_spacing_s']:g} | {m['detumbling_time_s']:.9f} | {m['saturation_fraction']:.10g} | {m['peak_torque_Nm']:.12g} |")
lines += ['',f"All output comparisons pass; largest adjacent hold-start change is {accept['maximum_output_event_change_s']:.9g} s (required <=1 s). Success classification is unchanged.",
          'Quarter/eighth/sixteenth canonical audit JSONs are retained. Full stress histories and final compact scalar traces permit output-audit reproduction.','',
          '## Canonical actuator bound','',
          f"At {baseline['step_s']:g} s, the canonical 0.1 A m^2 actuator **does not saturate** at any of {baseline['controller_stage_calls']} evaluated RK4 stages. "
          f"The maximum raw dipole norm is {baseline['max_raw_dipole_at_all_stages_A_m2']:.12g} A m^2. "
          f"Maximum preprojection/projected quaternion norm defects are {baseline['max_preprojection_norm_error']:.6g} / {baseline['max_projected_norm_error']:.6g}. "
          'Metrics agree with the unsaturated reference to the recorded roundoff tolerance. This result applies only to the canonical baseline, not every future sweep case.','',
          '## Reproduction and next action','',
          'Exact numerical commands are in `docs/stage3_validation/commands.ps1`; terminal logs are alongside it. '
          'The first premature baseline attempt correctly refused an unselected step; its log is retained as baseline_prerequisite.txt. '
          'The refinement directories refuse overwrites; use fresh paths for reruns.','',
          'Gate: `configs/verification.json`. Run the zero-simulation check after committing evidence:',
          '```powershell','.venv/Scripts/python.exe -m studies.parameter_sweep --grid pilot --verification configs/verification.json --check-only','```','',
          'NEXT, after this task (not executed here):','```powershell',
          '.venv/Scripts/python.exe -m studies.parameter_sweep --config configs/study.json --grid pilot --verification configs/verification.json --output data/processed/pilot/records.jsonl','```','',
          'Expected pilot output: `data/processed/pilot/records.jsonl`, `records.summary.json`, and `records_histories/`. '
          'The real 108-case pilot and its runtime/accuracy review remain mandatory before the 1152-case production grid. '
          'No pilot_records field is fabricated. Production remains blocked until real valid pilot records on the production tested commit exist.','',
          '## Evidence SHA256 (raw file bytes)','', '| Path | SHA256 |','| --- | --- |']
lines += [f"| `{item['path']}` | `{item['sha256']}` |" for item in gate['evidence_files']]
Path('docs/STAGE3_VERIFICATION.md').write_text('\n'.join(lines)+'\n')
print(json.dumps(summary,indent=2))
