import json
from pathlib import Path
import numpy as np
import pytest
from src.experiments import generate_cases, summarize
from studies.parameter_sweep import run, resolve_backend


def config(): return json.loads(Path('configs/study.json').read_text())


def test_counts_and_reproducibility():
    c=config();a=list(generate_cases(c));assert len(a)==108
    assert len(list(generate_cases(c,'production')))==1152
    assert a==list(generate_cases(c));assert len({x['case_id'] for x in a})==108
    same=[x for x in a if x['geometry_id']==0 and x['spin_deg_s']==1]
    assert all(x['y0']==same[0]['y0'] and x['phase_rad']==same[0]['phase_rad'] for x in same)
    for case in a:
        assert np.linalg.norm(case['y0'][:4])==pytest.approx(1)
        assert np.linalg.norm(case['y0'][4:])==pytest.approx(np.deg2rad(case['spin_deg_s']))


def test_paired_geometries():
    c=config();c['field_modes']=['orbital','frozen_inertial']
    a=list(generate_cases(c));assert len(a)==216
    assert a[0]['y0']==a[4]['y0'] and a[0]['phase_rad']==a[4]['phase_rad']


def test_censoring_and_invalid_denominator():
    s=summarize([dict(status='valid',metrics=dict(success=False,detumbling_time_s=None)),dict(status='invalid')])
    assert s['success_fraction']==0 and s['invalid']==1 and s['conditional_median_time_s'] is None


def test_gate_blocks_missing_evidence():
    with pytest.raises(ValueError,match='require'): resolve_backend(config(),None,'pilot')
    with pytest.raises(ValueError,match='not satisfied'): resolve_backend(config(),'configs/verification.example.json','pilot')


def test_fixture_pipeline_and_no_overwrite():
    import uuid
    tmp_path=Path("data/processed/test_runs")/uuid.uuid4().hex
    p=tmp_path/'fixture.jsonl';s=run('configs/study.json',p,'demo',True)
    rows=[json.loads(x) for x in p.read_text().splitlines()]
    assert s['total']==18 and s['invalid']==0
    assert all(r['synthetic'] for r in rows)
    assert all(Path(r['history']).exists() for r in rows)
    with pytest.raises(FileExistsError):run('configs/study.json',p,'demo',True)


def test_invalid_simulations_are_not_deadline_failures(monkeypatch):
    import uuid
    from studies import fixtures
    def broken(case, dt):
        raise RuntimeError("intentional test failure")
    monkeypatch.setattr(fixtures, "simulate", broken)
    p=Path("data/processed/test_runs")/uuid.uuid4().hex/"invalid.jsonl"
    s=run("configs/study.json",p,"demo",True)
    rows=[json.loads(x) for x in p.read_text().splitlines()]
    assert s["invalid"]==18 and s["valid"]==0
    assert s["success_fraction"] is None and s["censored"]==0
    assert all(r["metrics"] is None and "intentional" in r["failure_reason"] for r in rows)
