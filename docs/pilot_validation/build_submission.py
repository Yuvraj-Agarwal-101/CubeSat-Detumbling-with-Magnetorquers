"""Build measured 16-case study artifacts; never runs a simulation."""
import csv
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from studies import make_figures
from src.experiments import summarize
import numpy as np


def main():
    root = Path('data/processed/targeted')
    first = [json.loads(x) for x in (root/'first12.jsonl').read_text().splitlines()]
    extra = [json.loads(x) for x in (root/'additional.jsonl').read_text().splitlines()]
    rows = first+extra
    assert len(first) == 12 and len(extra) == 4 and len(rows) == 16
    (root/'records.jsonl').write_text(''.join(json.dumps(r,allow_nan=False)+'\n' for r in rows), newline='\n')
    subprocess.run([sys.executable,'docs/pilot_validation/validate_pilot.py'],check=True,stdout=(root/'validation_stdout.txt').open('w'))
    summary = json.loads((root/'validation.json').read_text())
    summary.update(scope='Final targeted 16-case engineering study; not an exhaustive sweep',
                   production_sweep_ready=False, production_blocker='108-case pilot intentionally discontinued at submission deadline; no production sweep authorized')
    (root/'summary.json').write_text(json.dumps(summary,indent=2)+'\n', newline='\n')
    figdir = Path('figures/targeted'); figdir.mkdir(exist_ok=True,parents=True)
    reportfig = Path('report/figures'); reportfig.mkdir(exist_ok=True)
    manifest = []
    plt = make_figures.plt
    def save(fig,name,caption,ids):
        fig.tight_layout()
        for ext in ('png','pdf'):
            path = figdir/(name+'.'+ext)
            fig.savefig(path,dpi=180,bbox_inches='tight')
            shutil.copyfile(path,reportfig/path.name)
        plt.close(fig)
        manifest.append(dict(figure=name,scope='TARGETED REAL ENGINEERING STUDY',caption=caption,
            records='data/processed/targeted/records.jsonl',case_ids=ids,
            command='.venv/Scripts/python.exe docs/pilot_validation/build_submission.py'))
    def history(r):
        with np.load(r['history']) as h:
            return {k:h[k].copy() for k in h.files}
    # Four shared geometries, using the smallest limit. The other limits give
    # exactly the same low-spin trajectories if their bounds remain inactive.
    fig,ax = plt.subplots(figsize=(7,3.8))
    for r,style in zip(first[:4],['-','--','-.',':']):
        h = history(r)
        ax.plot(h['t']/3600,np.rad2deg(np.linalg.norm(h['states'][:,4:],axis=1)),
                linestyle=style,label=f"Geometry {r['case']['geometry_id']}")
    ax.axhline(.5,color='black',lw=.8,label='0.5 deg/s threshold')
    ax.set(xlabel='Elapsed time [h]',ylabel='Angular-rate norm [deg/s]',
           title='Targeted study: geometry at 1 deg/s, gain 3e-6, limit 0.03 A m²')
    ax.legend(fontsize=8,ncol=2)
    save(fig,'targeted_geometry','Four seeded attitudes, spin directions and orbital phases; full six-orbit histories.',[r['case']['case_id'] for r in first[:4]])
    selected = [first[0]]+extra[:3]
    fig,axes = plt.subplots(1,2,figsize=(10,3.8))
    for r,style in zip(selected,['-','--','-.',':']):
        h = history(r); c=r['case']
        label=f"{c['spin_deg_s']} deg/s, gain {c['gain_kg_m2_s']:g}"
        rate=np.rad2deg(np.linalg.norm(h['states'][:,4:],axis=1))
        axes[0].semilogy(h['t']/3600,rate,linestyle=style,label=label)
        axes[1].plot(h['t']/3600,np.linalg.norm(h['dipole'],axis=1),linestyle=style,label=label)
    axes[0].axhline(.5,color='black',lw=.8)
    axes[0].set(xlabel='Elapsed time [h]',ylabel='Angular-rate norm [deg/s]')
    axes[1].set(xlabel='Elapsed time [h]',ylabel='Commanded dipole norm [A m²]')
    axes[0].legend(fontsize=7)
    fig.suptitle('Targeted matched spin/gain comparison: geometry 0, limit 0.03 A m²')
    save(fig,'targeted_spin_gain','Matched initial spin and gain comparisons at geometry 0; same actuator bound.',[r['case']['case_id'] for r in selected])
    fig,axes = plt.subplots(1,2,figsize=(9.5,3.8))
    for r,style in zip(extra[2:],['-','--']):
        h=history(r); label=f"Limit {r['case']['dipole_limit_Am2']:g} A m²"
        axes[0].semilogy(h['t']/3600,np.rad2deg(np.linalg.norm(h['states'][:,4:],axis=1)),linestyle=style,label=label)
        axes[1].plot(h['t']/3600,np.linalg.norm(h['raw_dipole'],axis=1)/r['case']['dipole_limit_Am2'],linestyle=style,label=label)
    axes[0].axhline(.5,color='black',lw=.8); axes[1].axhline(1,color='black',lw=.8)
    axes[0].set(xlabel='Elapsed time [h]',ylabel='Angular-rate norm [deg/s]')
    axes[1].set(xlabel='Elapsed time [h]',ylabel='Raw dipole norm / configured limit')
    axes[0].legend(fontsize=8)
    fig.suptitle('Targeted actuator comparison: 30 deg/s, gain 3e-5, geometry 0')
    save(fig,'targeted_actuator','Raw-to-limit ratios above one indicate saturation; commands remain bounded.',[r['case']['case_id'] for r in extra[2:]])
    columns=['case_id','spin_deg_s','gain_kg_m2_s','dipole_limit_Am2','geometry_id','phase_rad','success','censored','detumbling_time_s','saturation_fraction','peak_torque_Nm','final_rate_rad_s','runtime_s']
    with (root/'results_table.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=columns,lineterminator='\n');writer.writeheader()
        for r in rows:
            d={**r['case'],**r['metrics'],'runtime_s':r['runtime_s']}
            writer.writerow({k:d[k] for k in columns})
    lines=[r'\begin{tabular}{rrrrrrr}',r'\hline',
           r'Spin & Gain & Limit & Geometry & Recovery [s] & Sat. [\%] & Peak $\tau$ [$\mu$Nm] \\',r'\hline']
    for r in rows:
        c=r['case'];m=r['metrics'];time='censored' if m['detumbling_time_s'] is None else f"{m['detumbling_time_s']:.1f}"
        lines.append(f"{c['spin_deg_s']} & {c['gain_kg_m2_s']:g} & {c['dipole_limit_Am2']:g} & {c['geometry_id']} & {time} & {100*m['saturation_fraction']:.2f} & {1e6*m['peak_torque_Nm']:.3f} "+r'\\')
    lines += [r'\hline',r'\end{tabular}']
    Path('report/sections/targeted_results_table.tex').write_text('\n'.join(lines)+'\n', newline='\n')
    (figdir/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n', newline='\n')
    files=[root/'records.jsonl',root/'summary.json',root/'validation.json',root/'results_table.csv']
    files += [Path(r['history']) for r in rows]
    files += list(figdir.glob('*'))
    evidence=dict(scope=summary['scope'], tested_commit=rows[0]['tested_commit'],
        adapter='team_adapter:simulate',dt_s=.25,seed=3702026,
        configuration_sha256=summary['config_sha256'],
        artifact_sha256={str(p.as_posix()):hashlib.sha256(p.read_bytes()).hexdigest() for p in files})
    (root/'manifest.json').write_text(json.dumps(evidence,indent=2)+'\n', newline='\n')
    print(json.dumps({k:v for k,v in summary.items() if k not in ('history_checks','breakdowns')},indent=2))


if __name__ == '__main__':
    main()
