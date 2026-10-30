"""Combine measured canonical/stress refinements; never discard failed levels."""
import json
from pathlib import Path
import sys
import numpy as np
sys.path.insert(0,str(Path.cwd()))
from studies.timestep_selection import compare,select_step
from src.config import case_summary
from studies.complete_verification import trace_metrics

def read(p):
    return json.loads(Path(p).read_text())

root=Path('data/processed')
old=read(root/'timestep_selection.json')
coarse=read(root/'stage3_high_spin_audit/audit.json')
fine=read(root/'stage3_high_spin_fine_audit/audit.json')
case=coarse['case']; document=case['document']; timing=case_summary(document)
runs=[read(root/'stage3_high_spin_audit/coarse_2s.json')]
for audit,folder in [(coarse,'stage3_high_spin_audit'),(fine,'stage3_high_spin_fine_audit')]:
    for i,(step,metric) in enumerate(zip(audit['steps_s'],audit['metrics'])):
        with np.load(root/folder/f'level_{i}.npz') as h:
            record=dict(step_s=step,metrics=metric,runtime_s=audit['runtime_s'][i],
                        max_preprojection_norm_error=float(np.max(np.abs(h['preprojection_norm_error']))),
                        max_projected_norm_error=float(np.max(np.abs(np.linalg.norm(h['states'][:,:4],axis=1)-1))),
                        rhs_evaluations=4*(len(h['t'])-1))
        runs=[r for r in runs if r['step_s']!=step]+[record]
runs.sort(key=lambda r:-r['step_s'])
assert [r['step_s'] for r in runs]==old['settings']['step_sizes_s']
tolerances=old['settings']['tolerances']
stress=dict(name='high_spin',regime='saturated',config=document,
            y0=case['y0'],t_span=[0,timing['deadline_s']],seed=case['seed'],
            orbital_period_s=timing['orbital_period_s'],
            regime_check_pass=all(r['metrics']['saturation_fraction']>0 for r in runs),
            runs=runs,comparisons=[compare(a['metrics'],b['metrics'],tolerances) for a,b in zip(runs[:-1],runs[1:])],
            metric_definition='Person 4 piecewise linear event and saturation metrics at every integration level',
            geometry_id=case['geometry_id'],spin_deg_s=case['spin_deg_s'],
            callback_identifiers=dict(field_model='src.orbit_field:field_model',controller='src.controller:controller'))
old['cases']=[c for c in old['cases'] if c['name']!='high_spin']+[stress]
chosen=select_step(old['cases'],old['settings']['step_sizes_s'])
assert chosen is not None,'Additional high-spin refinement is required'
old.update(selected_step_s=chosen,status='confirmed numerical step including high-spin pilot setting')
(root/'timestep_selection.json').write_text(json.dumps(old,indent=2)+'\n')
confirmation=read(root/'production_validation/confirmation.json')
rows=[dict(output_spacing_s=step,metrics={k:m[k] for k in tolerances|{'success':None}})
      for step,m in zip(fine['steps_s'],fine['output_only_metrics'])]
with np.load(root/'stage3_high_spin_fine_audit/level_2.npz') as history:
    t=history['t']; rate=np.linalg.norm(history['states'][:,4:],axis=1)
    raw=np.linalg.norm(history['raw_dipole'],axis=1)
    torque=np.linalg.norm(history['torque'],axis=1)
    for stride,row in zip((4,2,1),rows):
        nodes=np.unique(np.r_[np.arange(0,len(t),stride),len(t)-1])
        independent=trace_metrics(t[nodes],rate[nodes],raw[nodes],torque[nodes],
                                 timing['rate_threshold_rad_s'],timing['hold_duration_s'],case['dipole_limit_Am2'])
        assert all(np.isclose(independent[k],v,rtol=1e-12,atol=1e-12)
                   if v is not None else independent[k] is None for k,v in row['metrics'].items())
    np.savez_compressed(root/'production_validation/high_spin_trace.npz',
                        t=t,rate_rad_s=rate,raw_dipole_norm=raw,torque_norm=torque)
output_comparisons=[compare(a['metrics'],b['metrics'],tolerances) for a,b in zip(rows[:-1],rows[1:])]
confirmation['cases']=[c for c in confirmation['cases'] if c['name']!='high_spin']+[
    dict(name='high_spin',run=runs[-1],output_audit=rows,output_comparisons=output_comparisons,
         person4_metric_agreement=True,person4_metrics=fine['output_only_metrics'],config=document,
         max_projected_norm_error=runs[-1]['max_projected_norm_error'])]
confirmation.update(selected_step_s=chosen,
    output_grid_pass=all(c['pass'] for case in confirmation['cases'] for c in case['output_comparisons']),
    scope='Canonical gain 1e-5 in both saturation regimes, plus seeded pilot geometry 0 at 30 deg/s, gain 3e-5, limit 0.03 A m^2. Finite numerical pilot-entry verification; no blanket approval of the engineering grid.')
(root/'production_validation/confirmation.json').write_text(json.dumps(confirmation,indent=2)+'\n')
print('Accepted common candidate:',chosen)
print('All comparisons:',[(c['name'],[x['pass'] for x in c['comparisons']]) for c in old['cases']])
