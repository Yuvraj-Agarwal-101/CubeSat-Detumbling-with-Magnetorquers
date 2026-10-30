from pathlib import Path
import subprocess,re,json
p=Path('report/sections/reproducibility.tex');s=p.read_text();s=re.sub(r'<<<<<<< HEAD\n.*?=======\n(.*?)>>>>>>> origin/aleksandar\n',lambda m:m[1],s,flags=re.S);p.write_text(s)
# Original acceptance is historical evidence, not a fresh approval of merged source.
paths=['src/dynamics.py','src/integrators.py','src/orbit_field.py','src/controller.py','team_adapter.py']
for path in paths:
 p=Path('docs/integration_sources/aleksandar')/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(subprocess.check_output(['git','show','origin/aleksandar:'+path]))
p=Path('data/processed/production_validation/acceptance.json');a=json.loads(p.read_text());a['source_revision']='7f0a3de';a['source_snapshot_root']='docs/integration_sources/aleksandar';a['integration_status']='Historical baseline evidence retained. Merged numerical architecture requires Person 3 verification before new production approval.';p.write_text(json.dumps(a,indent=2)+'\n')
p=Path('tests/test_production_evidence.py');s=p.read_text();s=s.replace("hashes=dict(evidence['evidence_sha256'],**evidence['physics_source_sha256'])", "hashes=evidence['evidence_sha256']\n    source_root=ROOT / evidence.get('source_snapshot_root', '')\n    for name,digest in evidence['physics_source_sha256'].items():\n        actual=hashlib.sha256((source_root/name).read_bytes().replace(b'\\r\\n',b'\\n')).hexdigest()\n        assert actual==digest\n        # Unmoved physics and adapter must still match the measured source.\n        if name not in ('src/dynamics.py','src/integrators.py'):\n            assert hashlib.sha256((ROOT/name).read_bytes().replace(b'\\r\\n',b'\\n')).hexdigest()==digest\n    assert evidence.get('integration_status', '').startswith('Historical baseline evidence retained.')")
p.write_text(s)
