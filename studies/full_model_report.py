"""Generate a numerical study table only from measured full model records."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def run():
    path=ROOT/'data/processed/timestep_selection.json'
    record=json.loads(path.read_text()) if path.exists() else {}
    text=r'\subsection{Full model numerical refinement}'+'\n'
    if not record.get('cases'):
        text+='The real field and controller are implemented. The full model refinement record has not yet been generated.\n'
    else:
        text+=r'''The study uses the implemented circular orbit, rotating tilted dipole,
normalized B dot control and vector norm saturation. Each case runs to six
orbital periods from the canonical initial state. The unsaturated limit is
$1\ \mathrm{A\,m^2}$ and the saturated limit is $0.01\ \mathrm{A\,m^2}$.
These are numerical verification choices, not revised baseline hardware claims.
\begin{center}
\begin{tabular}{lrrrrr}
Case & $h$ & Success & $t_d$ & Final rate & Saturation \\
\hline
'''
        for case in record['cases']:
            for run in case['runs']:
                m=run['metrics']; td='{}' if m['detumbling_time_s'] is None else f"{m['detumbling_time_s']:.2f}"
                text+=f"{case['name']} & {run['step_s']:g} & {int(m['success'])} & {td} & {m['final_rate_rad_s']:.6f} & {m['saturation_fraction']:.6f} "+chr(92)*2+'\n'
        text+=r'''\end{tabular}
\end{center}
Times and steps are in seconds, final rates in radians per second, and
saturation is a time fraction. Full precision records also include peak
torque, effort, runtime, evaluation counts and norm diagnostics.
'''
        selected=record['selected_step_s']
        if selected is None:
            text+='No tested step passed all declared comparisons across both cases. Further refinement is required.\n'
        else:
            text+=f'The screening gate selects ${selected:g}$ seconds for these two cases after two successive refinements.\n'
        text+=r'''The declared relative tolerances are one percent for time, final rate
and peak torque, with absolute floors of one second, $10^{-6}$ radians per
second and $10^{-10}$ newton metres. Saturation fraction uses $0.005$ absolute.
The JSON records every comparison and classification. Screening acceptance
does not approve every gain, initial geometry or case near a success boundary.
The metrics use sampled output; threshold intervals, saturation crossings
and narrow torque peaks can be unresolved. The independent output grid audit and accepted baseline setting are documented
in the next subsection. Broader engineering cases still require their own audit.
A deadline failure does not establish that eventual recovery is impossible.
'''
    (ROOT/'report/sections/full_model_verification.tex').write_text(text)


if __name__=='__main__':
    run()
