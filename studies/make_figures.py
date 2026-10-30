"""Regenerate monochrome convergence figures using the shared dependencies."""
from pathlib import Path
import json
import os
import tempfile
import shutil

# Keep disposable plotting caches out of the user's home and the repository.
_cache = tempfile.TemporaryDirectory(prefix='ae370-plot-')
os.environ.setdefault('MPLCONFIGDIR', _cache.name)
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]

def run():
    rows = json.loads((ROOT/'data/processed/convergence.json').read_text())['results']
    with plt.rc_context({'font.size': 10, 'text.color': 'black', 'axes.labelcolor': 'black'}):
        figure, axes = plt.subplots(1, 2, figsize=(10, 4.2), layout='constrained')
        for axis, case, title in zip(axes, ('scalar', 'spherical'),
                                     ('Scalar nonautonomous equation', 'Spherical torque free rotation')):
            subset = [r for r in rows if r['case'] == case]
            h = np.array([r['step_s'] for r in subset])
            error = np.array([r['error'] for r in subset])
            axis.loglog(h, error, 'ko-', markerfacecolor='white', label='Measured')
            axis.loglog(h, 1.8*error[0]*(h/h[0])**4, 'k--', label='Fourth order reference')
            axis.set(title=title, xlabel='Step size h (s)',
                     ylabel='Absolute error' if case == 'scalar' else 'Attitude error (rad)')
            axis.legend(frameon=False, fontsize=8)
        folder = ROOT/'figures'
        folder.mkdir(exist_ok=True)
        figure.savefig(folder/'convergence.png', dpi=180)
        report_figures = ROOT/'report/figures'
        report_figures.mkdir(exist_ok=True)
        shutil.copyfile(folder/'convergence.png', report_figures/'convergence.png')
        plt.close(figure)
    print('Wrote figures/convergence.png and the report copy')

if __name__ == '__main__':
    run()
