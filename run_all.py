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
    parser.add_argument('--settings',help='Full model refinement settings JSON')
    parser.add_argument('--complete-verification',action='store_true',
                        help='Expensive full reproduction of coarse/fine runs and baseline confirmation')
    args=parser.parse_args()
    start=time.perf_counter()
    out=ROOT/'data/processed'; out.mkdir(parents=True,exist_ok=True)
    subprocess.run([sys.executable,'-m','tools.export_report_inputs'], cwd=ROOT, check=True)
    check_command=[sys.executable,'-m','pytest','-q']
    if args.complete_verification:
        check_command+=['--ignore=tests/test_production_evidence.py']
    tests=subprocess.run(check_command,
                         cwd=ROOT,capture_output=True,text=True)
    log=tests.stdout+tests.stderr
    (out/'test_results.txt').write_text(log)
    print(log)
    if tests.returncode:
        raise SystemExit(tests.returncode)
    modules=['studies.verification','studies.convergence','studies.lecture_validation','studies.physics_verification','studies.make_figures']
    if args.complete_verification:
        subprocess.run([sys.executable,'-m','studies.timestep_selection','--adapter','team_adapter',
                        '--settings','configs/full_model_refinement.json'],cwd=ROOT,check=True)
        subprocess.run([sys.executable,'-m','studies.complete_verification'],cwd=ROOT,check=True)
        subprocess.run([sys.executable,'-m','studies.baseline_confirmation'],cwd=ROOT,check=True)
        subprocess.run([sys.executable,'-m','studies.production_acceptance','--apply'],cwd=ROOT,check=True)
    elif args.adapter:
        modules.append('studies.timestep_selection')
    modules.extend(['studies.full_model_report','studies.production_acceptance','studies.report_fragments'])
    for module in modules:
        command=[sys.executable,'-m',module]
        if module=='studies.timestep_selection' and args.adapter:
            command+=['--adapter',args.adapter]
            if args.settings:
                command+=['--settings',args.settings]
        subprocess.run(command,cwd=ROOT,check=True)
    if args.complete_verification:
        # The evidence consistency check belongs after regenerated acceptance.
        subprocess.run([sys.executable,'-m','tools.export_report_inputs'],cwd=ROOT,check=True)
        tests=subprocess.run([sys.executable,'-m','pytest','-q'],cwd=ROOT,capture_output=True,text=True)
        (out/'test_results.txt').write_text(tests.stdout+tests.stderr)
        print(tests.stdout+tests.stderr)
        if tests.returncode:
            raise SystemExit(tests.returncode)
    result=dict(status='Person 2 local workflow completed',
                full_model='rerun via real adapter' if args.adapter or args.complete_verification else 'not rerun; existing full model evidence retained',
                python=platform.python_version(),platform=platform.platform(),
                dependencies={n:importlib.metadata.version(n) for n in ['numpy','matplotlib','pytest']},
                command='python run_all.py'+(' --complete-verification' if args.complete_verification else '')+(' --adapter '+args.adapter if args.adapter else '')+(' --settings '+args.settings if args.settings else ''),
                elapsed_s=time.perf_counter()-start,seed=None,
                repository='https://github.com/Yuvraj-Agarwal-101/CubeSat-Detumbling-with-Magnetorquers',
                teammate_clean_clone_test='pending')
    (out/'run_summary.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))


if __name__=='__main__': main()
