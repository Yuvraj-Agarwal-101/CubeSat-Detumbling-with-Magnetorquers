from pathlib import Path
import subprocess,re

def source(ref,path): return subprocess.check_output(['git','show',f'{ref}:{path}'])
def write(path,data):
 p=Path(path);p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data if isinstance(data,bytes) else data.encode())
def resolve(path,choices):
 text=Path(path).read_text();i=iter(choices)
 text=re.sub(r'<<<<<<< HEAD\n(.*?)=======\n(.*?)>>>>>>> origin/aleksandar\n',lambda m:m.group(next(i)),text,flags=re.S)
 write(path,text)
# Retain provenance for overlapping measured records and source report drafts.
conflicts=subprocess.check_output(['git','diff','--name-only','--diff-filter=U'],text=True).splitlines()
for path in conflicts:
 for ref,label in [('origin/yuvraj','yuvraj'),('origin/aleksandar','aleksandar')]:
  write('docs/integration_sources/'+label+'/'+path,source(ref,path))
# Numerical architecture owns the shared method; physics additions are composed below.
for path in ['README.md','SHA256SUMS.txt','data/processed/convergence.csv','data/processed/convergence.json','data/processed/run_summary.json','data/processed/test_results.txt','docs/dynamics_interface.md','docs/person2_interface.md','docs/submission_readiness.md','report/PERSON2_FRAGMENTS.md','report/sections/acknowledgments.tex','report/sections/conclusions.tex','report/sections/contributions.tex','report/sections/method.tex','report/sections/numerical_verification.tex']:
 write(path,source('origin/yuvraj',path))
resolve('src/integrators.py',[1])
resolve('run_all.py',[2,2])
p=Path('run_all.py');p.write_text(p.read_text().replace("modules=['studies.convergence'","modules=['studies.verification','studies.convergence'"))
resolve('studies/report_fragments.py',[1,2,2])
p=Path('studies/report_fragments.py');p.write_text(p.read_text().replace("('method','verification','numerical_verification',","('method','verification','numerical_verification','person2_verification',").replace('The existing 175 quaternion','The quaternion'))
resolve('report/sections/verification.tex',[1])
p=Path('report/sections/verification.tex');p.write_text(p.read_text()+''.join('\\input{sections/'+x+'}\n' for x in ['lecture_alignment','physics_verification','full_model_verification','production_step']))
p=Path('report/sections/method.tex');s=p.read_text().replace('The production magnetic model has not yet been assembled, so it has not been established that its complete dynamics are nonstiff.','The idealized production magnetic model is implemented. Its complete nonlinear dynamics have not been established to be nonstiff across engineering cases.')
a=source('origin/aleksandar','report/sections/method.tex').decode();start=a.index('Following Lecture 12');end=a.index('After each completed step')
s+='\n\\subsection{Lecture stability interpretation and model scales}\n'+a[start:end];p.write_text(s)
for name in ['docs/dynamics_interface.md','docs/person2_interface.md']:
 p=Path(name);p.write_text(p.read_text()+'\n## Integrated field and controller\n\nThe real idealized orbital field, normalized B-dot controller and team_adapter are implemented. Existing baseline step evidence is retained at data/processed/production_validation; the 1 s step applies only to the recorded baseline and regimes. Broader sweep verification remains pending. Both numerical APIs remain available. See docs/INTEGRATION.md for merged validation and evidence provenance.\n')
