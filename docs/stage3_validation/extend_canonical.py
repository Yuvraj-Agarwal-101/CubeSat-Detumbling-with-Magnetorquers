"""Extend both real six-orbit regimes, preserving each output audit."""
from pathlib import Path
import shutil
import subprocess
import sys

folder=Path('data/processed/production_validation')
for step,label in [(.25,'quarter'),(.125,'eighth'),(.0625,'sixteenth')]:
    if step != .25:
        subprocess.run([sys.executable,'-m','studies.complete_verification',
                        '--fine-step',str(step)],check=True)
    for name in ['confirmation','unsaturated','saturated']:
        shutil.copyfile(folder/(name+'.json'),folder/(name+'_'+label+'.json'))
