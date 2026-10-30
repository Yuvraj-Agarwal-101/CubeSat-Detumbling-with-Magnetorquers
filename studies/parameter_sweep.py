"""CLI sweep with explicit physics adapter and evidence gates."""
import argparse
import hashlib
import importlib
import json
from pathlib import Path
import subprocess
import time
import traceback
import numpy as np
from src.experiments import generate_cases, summarize
from src.metrics import compute_metrics


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def resolve_backend(config, gate_path, grid):
    if not gate_path:
        raise ValueError('Real simulations require --verification from Person 2')
    gate=json.loads(Path(gate_path).read_text())
    for key in ('independent_physics_checks_passed','smooth_convergence_passed',
                'output_grid_refinement_passed','person2_accepted'):
        if gate.get(key) is not True:
            raise ValueError('Verification gate not satisfied: '+key)
    for key in ('evidence_files','accepted_by','adapter','dt_s'):
        if not gate.get(key): raise ValueError('Missing gate field: '+key)
    for item in gate['evidence_files']:
        if digest(item['path']) != item['sha256']:
            raise ValueError('Evidence hash mismatch: '+item['path'])
    commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    if gate.get('tested_commit') != commit:
        raise ValueError('Verification must identify the current tested commit')
    if subprocess.check_output(['git','status','--porcelain','--untracked-files=no'],text=True).strip():
        raise ValueError('Commit tracked changes before real study verification')
    if grid == 'production':
        pilot_path=gate.get('pilot_records')
        if not pilot_path: raise ValueError('Production requires pilot_records')
        pilot=[json.loads(x) for x in Path(pilot_path).read_text().splitlines()]
        if (len(pilot)!=108 or any(r['synthetic'] or r['status']!='valid' for r in pilot)
                or any(r['tested_commit']!=commit for r in pilot)):
            raise ValueError('Production requires 108 valid real pilot cases on tested commit')
    module, function=gate['adapter'].split(':')
    dt=float(gate['dt_s'])
    if not np.isfinite(dt) or dt <= 0: raise ValueError('invalid accepted step')
    return getattr(importlib.import_module(module),function),dt,gate


def run(config_path, output, grid='pilot', synthetic=False, verification=None):
    config=json.loads(Path(config_path).read_text())
    if synthetic:
        from studies.fixtures import simulate
        dt=30.;gate=None
    else:
        simulate,dt,gate=resolve_backend(config,verification,grid)
    output=Path(output)
    output.parent.mkdir(parents=True,exist_ok=True)
    if output.exists(): raise FileExistsError('Refusing to overwrite '+str(output))
    histories=output.parent/(output.stem+'_histories');histories.mkdir(exist_ok=False)
    records=[]
    commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    start=time.perf_counter()
    with output.open('w',encoding='utf-8') as f:
        for case in generate_cases(config,grid):
            then=time.perf_counter()
            record=dict(case=case,synthetic=synthetic,dt_s=dt,tested_commit=commit,
                        config_sha256=digest(config_path),verification=gate)
            try:
                result=simulate(case,dt)
                metrics=compute_metrics(**{k:result[k] for k in
                    ('t','states','raw_dipole','dipole','torque')},
                    settings=case['metrics'],limit=case['dipole_limit_Am2'])
                path=histories/(case['case_id']+'.npz')
                np.savez_compressed(path,**result)
                record.update(status='valid',metrics=metrics,history=str(path.as_posix()),failure_reason=None)
            except Exception as exc:
                record.update(status='invalid',metrics=None,failure_reason=f'{type(exc).__name__}: {exc}',
                              traceback=traceback.format_exc())
            record['runtime_s']=time.perf_counter()-then
            records.append(record);f.write(json.dumps(record,allow_nan=False)+'\n');f.flush()
    summary=summarize(records)
    summary.update(synthetic=synthetic,runtime_s=time.perf_counter()-start,
                   mean_case_runtime_s=float(np.mean([r['runtime_s'] for r in records])),
                   proposed_1152_runtime_s=float(np.mean([r['runtime_s'] for r in records])*1152))
    output.with_suffix('.summary.json').write_text(json.dumps(summary,indent=2))
    return summary


def main():
    p=argparse.ArgumentParser();p.add_argument('--config',default='configs/study.json')
    p.add_argument('--output',required=True);p.add_argument('--grid',choices=['pilot','production','demo','paired'],default='pilot')
    p.add_argument('--synthetic',action='store_true');p.add_argument('--verification')
    a=p.parse_args();print(json.dumps(run(a.config,a.output,a.grid,a.synthetic,a.verification),indent=2))


if __name__=='__main__': main()
