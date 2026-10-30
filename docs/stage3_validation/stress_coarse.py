"""Retain the two-second high-spin comparison alongside all finer levels."""
import json
from pathlib import Path
import sys
import time
import numpy as np
sys.path.insert(0,str(Path.cwd()))
from src.experiments import generate_cases
from src.metrics import compute_metrics
from team_adapter import simulate

case=list(generate_cases(json.loads(Path('configs/study.json').read_text())))[96]
start=time.perf_counter()
history=simulate(case,2.)
metrics=compute_metrics(**{k:history[k] for k in ('t','states','raw_dipole','dipole','torque')},
                        settings=case['metrics'],limit=case['dipole_limit_Am2'])
record=dict(step_s=2.,metrics=metrics,runtime_s=time.perf_counter()-start,
            max_preprojection_norm_error=float(np.max(np.abs(history['preprojection_norm_error']))),
            max_projected_norm_error=float(np.max(np.abs(np.linalg.norm(history['states'][:,:4],axis=1)-1))),
            rhs_evaluations=4*(len(history['t'])-1))
out=Path('data/processed/stage3_high_spin_audit')
np.savez_compressed(out/'coarse_2s.npz',**history)
(out/'coarse_2s.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record,indent=2))
