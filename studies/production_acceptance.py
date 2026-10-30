"""Apply a production step only after state, metric, output and baseline checks."""
import hashlib
import json
from pathlib import Path
from src.config import load_config, validate_config
from studies.timestep_selection import select_step

ROOT=Path(__file__).resolve().parents[1]


def apply():
    record=json.loads((ROOT/'data/processed/timestep_selection.json').read_text())
    audit=json.loads((ROOT/'data/processed/production_validation/confirmation.json').read_text())
    baseline=json.loads((ROOT/'data/processed/production_validation/baseline.json').read_text())
    hashes=record.get('source_hashes') or json.loads((ROOT/'data/processed/field_control_validation.json').read_text())['source_hashes']
    for name,expected in hashes.items():
        if hashlib.sha256((ROOT/name).read_bytes().replace(b'\r\n',b'\n')).hexdigest()!=expected:
            raise ValueError('Verification evidence does not match current physics code: '+name)
    chosen=select_step(record['cases'],record['settings']['step_sizes_s'])
    if chosen is None or chosen!=audit['selected_step_s'] or not audit['output_grid_pass']:
        raise ValueError('Both successive metric refinements and output resolution must pass')
    output_changes=[]
    for case in audit['cases']:
        for a,b in zip(case['output_audit'][:-1],case['output_audit'][1:]):
            ta,tb=a['metrics']['detumbling_time_s'],b['metrics']['detumbling_time_s']
            if ta is None or tb is None:
                raise ValueError('Successful event timing is required for this baseline validation')
            output_changes.append(abs(ta-tb))
    if max(output_changes)>1.:
        raise ValueError('Output event timing has not converged to one second')
    if not baseline['bound_inactive_at_all_stages'] or not baseline['reference_unsaturated_metrics_agree']:
        raise ValueError('Canonical baseline confirmation failed')
    document=load_config()
    for key in ['physical','initial_conditions','study']:
        if document[key]!=baseline['configuration'][key]:
            raise ValueError('Baseline physics or mission criteria changed')
    document['solver']['step_size_s']=chosen
    document['provenance']['solver.step_size_s']=dict(classification='derived',
        note='Accepted from two successive real-model refinements and independent output sampling audit; see data/processed/production_validation/acceptance.json. Applies to the stated baseline and tested saturation regimes.')
    validate_config(document)
    (ROOT/'configs/baseline.json').write_text(json.dumps(document,indent=2)+'\n')
    paths=['data/processed/timestep_selection.json','data/processed/production_validation/confirmation.json',
           'data/processed/production_validation/baseline.json']
    result=dict(status='numerical verification complete',accepted_step_s=chosen,
        accepted_by='Automated numerical checks executed by Codex at the user request',
        student_review='Not claimed; students must review and understand the generated work',
        scope=audit['scope'],baseline_max_raw_dipole_A_m2=baseline['max_raw_dipole_at_all_stages_A_m2'],
        maximum_output_event_change_s=max(output_changes),output_event_absolute_tolerance_s=1.,
        baseline_checks=baseline['controller_stage_calls'],
        physics_source_sha256=hashes,
        evidence_sha256={p:hashlib.sha256((ROOT/p).read_bytes().replace(b'\r\n',b'\n')).hexdigest() for p in paths},
        limitations='Finite sampled verification for declared physical settings; other sweep gains, rates and geometries require their own numerical audit. This is not final team submission approval.')
    (ROOT/'data/processed/production_validation/acceptance.json').write_text(json.dumps(result,indent=2)+'\n')
    print('Accepted numerical production step:',chosen)
    return result


def report():
    path=ROOT/'data/processed/production_validation/acceptance.json'
    if not path.exists():
        return
    accepted=json.loads(path.read_text());audit=json.loads((path.parent/'confirmation.json').read_text())
    historical=bool(accepted.get('source_snapshot_root'))
    text=(r'\paragraph{Historical source evidence} '+'The one second acceptance and measurements below belong to the original source snapshot. The merged numerical architecture requires renewed verification before new production approval.'+'\n' if historical else '')
    text+=r'''\subsection{Accepted numerical production step}
The production setting in the canonical configuration is
'''+f"${accepted['accepted_step_s']:g}$ second.\n"+r'''The two successive comparisons from one to half a second and from half to
a quarter second pass every declared metric tolerance in both saturation
regimes. Success classification remains unchanged. The earlier two second
saturated failure is retained in the record rather than discarded.

To separate output sampling from integration error, each quarter second
trajectory is held fixed while output spacing is coarsened. Complete hold
intervals use piecewise linear interpolation of rate norm, and saturation
duration uses crossings of the raw dipole norm. Equality qualifies in this
diagnostic, matching the Person 4 convention; the original sampled strict
threshold metric is retained for the integrator comparisons.
\begin{center}
\begin{tabular}{lrrr}
Case & Output spacing & Interpolated start & Saturation fraction \\
\hline
'''
    for case in audit['cases']:
        for row in case['output_audit']:
            m=row['metrics']
            text+=f"{case['name']} & {row['output_spacing_s']:g} & {m['detumbling_time_s']:.6f} & {m['saturation_fraction']:.8f} "+chr(92)*2+'\n'
    text+=r'''\end{tabular}
\end{center}
All output comparisons pass the same predeclared tolerances. Interpolation
does not prove that every continuous excursion was resolved, but refinement
supports the event resolution for these trajectories. Compact scalar
histories are supplied to reproduce this audit without reintegration.

The canonical $0.1\ \mathrm{A\,m^2}$ baseline is also integrated separately
at the accepted step. Its command bound is inactive at every evaluated RK4
stage. The maximum raw magnitude is
'''+f"${accepted['baseline_max_raw_dipole_A_m2']:.8f}$ ampere square metres across {accepted['baseline_checks']} stage calls.\n"+r'''Its metrics agree with the unsaturated reference to floating point
roundoff. This connects the unsaturated refinement case to the actual
baseline bound. Final contribution percentages, independent teammate
reproduction and the engineering sweep remain team responsibilities.
'''
    (ROOT/'report/sections/production_step.tex').write_text(text)


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--apply',action='store_true')
    args=parser.parse_args()
    if args.apply:
        apply()
    report()
