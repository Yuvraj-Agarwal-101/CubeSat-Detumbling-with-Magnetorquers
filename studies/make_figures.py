"""Monochrome figures from persisted records; fixture outputs visibly labeled."""
import argparse
import itertools
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from src.experiments import summarize


def generate(records_path, outdir):
    rows=[json.loads(x) for x in Path(records_path).read_text().splitlines()]
    if not rows: raise ValueError('empty records')
    if len({r['synthetic'] for r in rows}) != 1: raise ValueError('mixed real and synthetic records')
    out=Path(outdir);out.mkdir(parents=True,exist_ok=True)
    synthetic=rows[0]['synthetic']
    prefix='SYNTHETIC FIXTURE ONLY\n' if synthetic else ''
    manifest=[]
    def save(fig,name,description):
        fig.suptitle(prefix+description,fontsize=10)
        fig.tight_layout(rect=(0,0,1,.91))
        fig.savefig(out/(name+'.pdf'));fig.savefig(out/(name+'.png'),dpi=140)
        plt.close(fig)
        manifest.append(dict(figure=name+'.pdf',records=Path(records_path).as_posix(),
             command=f'python -m studies.make_figures --records {records_path} --output {outdir}',
             synthetic=synthetic,description=description,
             seeds=sorted({r['case']['seed'] for r in rows}),
             configs=sorted({r['config_sha256'] for r in rows})))
    orbital=[r for r in rows if r['case']['field_mode']=='orbital']
    gains=sorted({r['case']['gain_kg_m2_s'] for r in orbital})
    spins=sorted({r['case']['spin_deg_s'] for r in orbital})
    limits=sorted({r['case']['dipole_limit_Am2'] for r in orbital})
    groups=[]
    for gain,spin,limit in itertools.product(gains,spins,limits):
        subset=[r for r in orbital if (r['case']['gain_kg_m2_s'],r['case']['spin_deg_s'],r['case']['dipole_limit_Am2'])==(gain,spin,limit)]
        groups.append(dict(gain=gain,spin=spin,limit=limit,**summarize(subset)))
    (out/'summary_table.json').write_text(json.dumps(groups,indent=2))
    for gain in gains:
        fig,axes=plt.subplots(1,2,figsize=(10,4))
        for ax,metric,title in zip(axes,['conditional_median_time_s','success_fraction'],['Median time conditional on success [s]','Success fraction of valid cases']):
            z=np.full((len(spins),len(limits)),np.nan)
            for i,spin in enumerate(spins):
                for j,limit in enumerate(limits):
                    g=next(x for x in groups if (x['gain'],x['spin'],x['limit'])==(gain,spin,limit))
                    value=g[metric];z[i,j]=np.nan if value is None else value
                    label=f"{g['successes']}/{g['valid']}"
                    if g['invalid']: label+=f"\n{g['invalid']} invalid"
                    if metric=='conditional_median_time_s': label=('censored' if value is None else f'{value:.0f}')+'\n'+label
                    ax.text(j,i,label,ha='center',va='center',fontsize=7,
                            bbox=dict(facecolor='white',edgecolor='none',alpha=.85))
            image=ax.imshow(np.ma.masked_invalid(z),cmap='Greys',aspect='auto',origin='lower',**({'vmin':0,'vmax':1} if metric=='success_fraction' else {}))
            ax.set_xticks(range(len(limits)),[str(x) for x in limits]);ax.set_yticks(range(len(spins)),[str(x) for x in spins])
            ax.set_xlabel('Dipole limit [A m²]');ax.set_ylabel('Initial spin [deg/s]');ax.set_title(title,fontsize=9)
            fig.colorbar(image,ax=ax)
        save(fig,f'maps_gain_{gain:g}',f'Orbital field, gain {gain:g} kg m²/s; labels show successes/valid')
    fig,axes=plt.subplots(1,2,figsize=(10,4))
    for i,limit in enumerate(limits):
        fractions=[];saturations=[]
        for gain in gains:
            sub=[r for r in orbital if r['case']['gain_kg_m2_s']==gain and r['case']['dipole_limit_Am2']==limit]
            fractions.append(summarize(sub)['success_fraction'])
            sat=[r['metrics']['saturation_fraction'] for r in sub if r['status']=='valid']
            saturations.append(np.mean(sat) if sat else np.nan)
        for ax,y in zip(axes,[fractions,saturations]):
            ax.plot(gains,y,color='black',linestyle=['-','--',':','-.'][i%4],marker=['o','s','^','x'][i%4],label=f'{limit:g} A m²')
            ax.set_xscale('log');ax.set_xlabel('Gain [kg m²/s]');ax.set_ylim(-.03,1.03);ax.legend(fontsize=7)
    axes[0].set_ylabel('Success fraction of valid cases');axes[1].set_ylabel('Mean time weighted saturation fraction')
    save(fig,'gain_saturation','Common ensemble across gains; aggregated over initial spins')
    index={}
    for r in rows:
        c=r['case'];key=(c['spin_deg_s'],c['gain_kg_m2_s'],c['dipole_limit_Am2'],c['geometry_id'])
        index.setdefault(key,{})[c['field_mode']]=r
    pairs=[v for v in index.values() if 'orbital' in v and 'frozen_inertial' in v]
    if pairs:
        fig,ax=plt.subplots(figsize=(5,4))
        both=[v for v in pairs if all(r['status']=='valid' and r['metrics']['success'] for r in v.values())]
        ax.scatter([v['frozen_inertial']['metrics']['detumbling_time_s'] for v in both],
                   [v['orbital']['metrics']['detumbling_time_s'] for v in both],color='black',marker='x')
        ax.set_xlabel('Frozen inertial field time [s]');ax.set_ylabel('Orbital field time [s]')
        ax.text(.03,.97,f'{len(both)}/{len(pairs)} pairs succeed in both',transform=ax.transAxes,va='top')
        save(fig,'paired_fields','Paired geometry comparison; times conditional on success in both')
        (out/'paired_outcomes.json').write_text(json.dumps([
            dict(key=list(k),outcomes={mode:dict(status=r['status'],metrics=r['metrics']) for mode,r in v.items()})
            for k,v in index.items()],indent=2))
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2))
    return manifest


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--records',required=True);p.add_argument('--output',required=True)
    a=p.parse_args();generate(a.records,a.output)
