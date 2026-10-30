"""Regenerate all delivered Person 2 results, not the unavailable team sweep."""
from pathlib import Path
import argparse
import importlib.metadata
import json
import platform
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parent


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--adapter',help='Full model adapter module, when available')
    args=parser.parse_args()
    start=time.perf_counter()
    out=ROOT/'data/processed'; out.mkdir(parents=True,exist_ok=True)
    subprocess.run([sys.executable,'-m','tools.export_report_inputs'], cwd=ROOT, check=True)
    tests=subprocess.run([sys.executable,'-m','pytest','-q'],
                         cwd=ROOT,capture_output=True,text=True)
    log=tests.stdout+tests.stderr
    (out/'test_results.txt').write_text(log)
    print(log)
    if tests.returncode:
        raise SystemExit(tests.returncode)
    modules=['studies.convergence','studies.lecture_validation','studies.make_figures','studies.report_fragments',
             'studies.timestep_selection']
    for module in modules:
        command=[sys.executable,'-m',module]
        if module=='studies.timestep_selection' and args.adapter:
            command+=['--adapter',args.adapter]
        subprocess.run(command,cwd=ROOT,check=True)
    result=dict(status='Person 2 local workflow completed',
                full_model='requested via adapter' if args.adapter else 'pending, no model supplied',
                python=platform.python_version(),platform=platform.platform(),
                dependencies={n:importlib.metadata.version(n) for n in ['numpy','matplotlib','pytest']},
                command='python run_all.py'+(' --adapter '+args.adapter if args.adapter else ''),
                elapsed_s=time.perf_counter()-start,seed=None,
                repository='https://github.com/Yuvraj-Agarwal-101/CubeSat-Detumbling-with-Magnetorquers',
                teammate_clean_clone_test='pending')
    (out/'run_summary.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))


if __name__=='__main__': main()
