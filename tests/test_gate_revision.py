"""A committed evidence gate may follow, but never change, tested source."""
import subprocess
import pytest
from studies.parameter_sweep import source_tree, verify_revision


def git(*args):
    return subprocess.check_output(['git',*args],text=True).strip()


def commit():
    git('add','.')
    git('-c','user.name=Gate test','-c','user.email=gate@example.invalid',
        'commit','-qm','test snapshot')
    return git('rev-parse','HEAD')


@pytest.fixture
def snapshot(tmp_path,monkeypatch):
    monkeypatch.chdir(tmp_path)
    git('init','-q')
    (tmp_path/'src').mkdir()
    (tmp_path/'src/model.py').write_text('verified = True\n')
    tested=commit()
    return tmp_path,dict(tested_commit=tested,tested_source_tree=source_tree(tested))


def test_evidence_commit_preserves_exact_source(snapshot):
    path,gate=snapshot
    (path/'evidence.json').write_text('{}')
    current=commit()
    assert current != gate['tested_commit']
    verify_revision(gate,current)


@pytest.mark.parametrize('change',['modify','add','delete','omit_manifest','forge_manifest'])
def test_source_change_or_incomplete_manifest_invalidates_gate(snapshot,change):
    path,gate=snapshot
    if change == 'modify':
        (path/'src/model.py').write_text('verified = False\n')
    elif change == 'add':
        (path/'src/new.py').write_text('new = True\n')
    elif change == 'delete':
        (path/'src/model.py').unlink()
    else:
        (path/'evidence.json').write_text('{}')
        if change == 'omit_manifest':
            gate.pop('tested_source_tree')
        else:
            gate['tested_source_tree']={'src/model.py':'forged'}
    current=commit()
    with pytest.raises(ValueError,match='current tested commit'):
        verify_revision(gate,current)
