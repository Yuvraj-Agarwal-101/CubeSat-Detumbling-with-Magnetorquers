"""Reproduce verified engineering studies or an explicitly synthetic demonstration."""
import argparse
from pathlib import Path
import subprocess
import sys


def main():
    p=argparse.ArgumentParser();p.add_argument('--demo',action='store_true')
    p.add_argument('--verification');p.add_argument('--output',default=None)
    a=p.parse_args()
    if not a.demo and not a.verification:
        p.error('Real report results pending upstream verification; use --verification or --demo')
    root=Path(__file__).resolve().parent
    def call(*args):subprocess.run([sys.executable,*args],cwd=root,check=True)
    call('-m','pytest','-q','-p','no:cacheprovider')
    out=Path(a.output or ('data/processed/synthetic_demo' if a.demo else 'data/processed/production'))
    flags=['--synthetic'] if a.demo else ['--verification',a.verification]
    call('-m','studies.parameter_sweep','--grid','demo' if a.demo else 'production',
         '--output',str(out/'records.jsonl'),*flags)
    call('-m','studies.make_figures','--records',str(out/'records.jsonl'),'--output',str(out/'figures'))
    call('-m','studies.parameter_sweep','--config','configs/paired.json','--grid','demo' if a.demo else 'paired',
         '--output',str(out/'paired.jsonl'),*flags)
    call('-m','studies.make_figures','--records',str(out/'paired.jsonl'),'--output',str(out/'paired_figures'))


if __name__=='__main__':main()
