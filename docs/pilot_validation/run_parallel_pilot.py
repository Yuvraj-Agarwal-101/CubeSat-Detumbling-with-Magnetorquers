"""Process-parallel targeted study through the real parameter_sweep runner.

Each worker calls the unchanged gated runner for one intended case. Ordered
aggregation preserves all records, including invalid simulations. No physics,
integration, event detection, timestep, or production grid is changed.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import json
import os
from pathlib import Path
import sys
import time

os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['OMP_NUM_THREADS'] = '1'
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from src.experiments import generate_cases, summarize
from studies import parameter_sweep


def worker(args):
    index, case, output = args
    parameter_sweep.generate_cases = lambda config, grid: iter([case])
    path = Path(output).parent/'shards'/f'{index:03d}'/'records.jsonl'
    parameter_sweep.run('configs/study.json', path, 'pilot', False, 'configs/verification.json')
    return index, json.loads(path.read_text())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--output', default='data/processed/reproduction16/records.jsonl')
    parser.add_argument('--indices', default='0,1,2,3,4,5,6,7,8,9,10,11,72,24,96,104',
                        help='Explicit comma-separated design indices; defaults to final 16-case study')
    args = parser.parse_args()
    config = json.loads(Path('configs/study.json').read_text())
    parameter_sweep.resolve_backend(config, 'configs/verification.json', 'pilot')
    cases = list(generate_cases(config, 'pilot'))
    assert len(cases) == 108
    indices = [int(x) for x in args.indices.split(',')]
    if len(set(indices)) != len(indices) or any(i < 0 or i >= 108 for i in indices):
        raise ValueError('Indices must be unique members of the 108-case design')
    if len(indices) > 24:
        raise ValueError('Targeted-study helper is capped at 24 cases; no full sweep')
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():
        raise FileExistsError(out)
    start = time.perf_counter()
    rows = {}
    with (out.parent/'progress.jsonl').open('w') as progress:
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            futures = [pool.submit(worker, (i,cases[i],args.output)) for i in indices]
            for future in as_completed(futures):
                index, row = future.result()
                rows[index] = row
                event = dict(index=index, case_id=row['case']['case_id'], status=row['status'],
                             completed=len(rows), elapsed_s=time.perf_counter()-start)
                progress.write(json.dumps(event)+'\n'); progress.flush()
                print(json.dumps(event), flush=True)
    ordered = [rows[i] for i in indices]
    out.write_text(''.join(json.dumps(r,allow_nan=False)+'\n' for r in ordered))
    summary = summarize(ordered)
    elapsed = time.perf_counter()-start
    mean = sum(r['runtime_s'] for r in ordered)/len(ordered)
    summary.update(synthetic=False, runtime_s=elapsed, workers=args.workers,
                   mean_case_runtime_s=mean,
                   runtime_note='Case runtimes measured under concurrent load; parallel estimate assumes same worker count and hardware.')
    out.with_suffix('.summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary), flush=True)


if __name__ == '__main__':
    main()
