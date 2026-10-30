"""Independent final 16-case targeted-study audit; run from repository root."""
import hashlib
import json
from pathlib import Path
import sys

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from src.experiments import generate_cases, summarize
from src.metrics import compute_metrics


def main():
    root = Path('data/processed/targeted')
    rows = [json.loads(x) for x in (root/'records.jsonl').read_text().splitlines()]
    expected = list(generate_cases(json.loads(Path('configs/study.json').read_text())))
    indices = list(range(12))+[72,24,96,104]
    assert len(rows) == len(indices) == 16
    assert [r['case'] for r in rows] == [expected[i] for i in indices]
    gate = json.loads(Path('configs/verification.json').read_text())
    hashes = {p: hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in
              ('configs/study.json', 'configs/baseline.json', 'configs/verification.json')}
    checks = []
    for r in rows:
        assert not r['synthetic'] and r['dt_s'] == .25 and r['verification'] == gate
        assert r['tested_commit'] == '56f7d04a57ef5c26d60b3ee796626ae1bb43f4e1'
        assert r['config_sha256'] == hashes['configs/study.json']
        assert r['baseline_sha256'] == hashes['configs/baseline.json']
        assert gate['adapter'] == 'team_adapter:simulate'
        assert r['status'] == 'valid', r.get('failure_reason')
        with np.load(r['history']) as h:
            assert all(np.isfinite(h[k]).all() for k in h.files)
            assert h['t'][0] == 0 and h['t'][-1] == r['case']['metrics']['deadline_s']
            assert np.max(np.diff(h['t'])) <= .25
            qerr = float(np.max(abs(np.linalg.norm(h['states'][:, :4], axis=1)-1)))
            assert qerr < 1e-12
            ratio = float(np.max(np.linalg.norm(h['dipole'], axis=1))/r['case']['dipole_limit_Am2'])
            assert ratio <= 1+1e-10
            m = compute_metrics(**{k:h[k] for k in ('t','states','raw_dipole','dipole','torque')},
                                settings=r['case']['metrics'], limit=r['case']['dipole_limit_Am2'])
            assert m == r['metrics']
            assert m['success'] == (m['detumbling_time_s'] is not None) == (not m['censored'])
            assert 0 <= m['saturation_fraction'] <= 1
            if m['success']:
                assert m['detumbling_time_s']+600 <= h['t'][-1]
            checks.append(dict(case_id=r['case']['case_id'], quaternion_norm_error=qerr,
                               max_command_limit_ratio=ratio,
                               max_preprojection_norm_error=float(np.max(abs(h['preprojection_norm_error']))),
                               samples=len(h['t']), end_s=float(h['t'][-1])))
    result = summarize(rows)
    result.update(config_sha256=hashes, tested_commits=sorted({r['tested_commit'] for r in rows}),
                  history_checks=checks)
    times = [r['metrics']['detumbling_time_s'] for r in rows if r['metrics']['success']]
    result['detumbling_time_range_s'] = [min(times), max(times)] if times else None
    for key in ('saturation_fraction', 'peak_torque_Nm', 'final_rate_rad_s'):
        values = [r['metrics'][key] for r in rows]
        result[key+'_range'] = [min(values), max(values)]
    result['runtime_s'] = {k:float(f([r['runtime_s'] for r in rows])) for k,f in
                           [('min',np.min), ('median',np.median), ('mean',np.mean), ('max',np.max), ('sum',np.sum)]}
    result['breakdowns'] = {}
    for key in ('spin_deg_s','gain_kg_m2_s','dipole_limit_Am2','geometry_id'):
        result['breakdowns'][key] = []
        for value in sorted({r['case'][key] for r in rows}):
            group = [r for r in rows if r['case'][key] == value]
            result['breakdowns'][key].append(dict(value=value, **summarize(group),
                mean_saturation=float(np.mean([r['metrics']['saturation_fraction'] for r in group]))))
    (root/'validation.json').write_text(json.dumps(result, indent=2)+'\n', newline='\n')
    print(json.dumps({k:v for k,v in result.items() if k != 'history_checks'}, indent=2))


if __name__ == '__main__':
    main()
