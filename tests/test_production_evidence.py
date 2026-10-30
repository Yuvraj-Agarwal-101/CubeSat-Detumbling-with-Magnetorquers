"""The operational setting must stay tied to real, reproducible evidence."""
import hashlib
import json
from pathlib import Path
from src.config import load_config, solver_settings

ROOT=Path(__file__).resolve().parents[1]


def test_production_setting_matches_accepted_evidence_and_physics():
    evidence=json.loads((ROOT/'data/processed/production_validation/acceptance.json').read_text())
    baseline=json.loads((ROOT/'data/processed/production_validation/baseline.json').read_text())
    current=load_config()
    assert solver_settings(current,require_step=True)['step_size_s']==evidence['accepted_step_s']
    assert evidence['maximum_output_event_change_s']<=evidence['output_event_absolute_tolerance_s']
    for key in ['physical','initial_conditions','study']:
        assert current[key]==baseline['configuration'][key]
    hashes=dict(evidence['evidence_sha256'],**evidence['physics_source_sha256'])
    for name,digest in hashes.items():
        actual=hashlib.sha256((ROOT/name).read_bytes().replace(b'\r\n',b'\n')).hexdigest()
        assert actual==digest
