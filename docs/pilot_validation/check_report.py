"""Static Overleaf packaging checks; no LaTeX compilation is claimed."""
import json
from pathlib import Path
import re
import zipfile


def main():
    root = Path('report')
    seen = set()
    missing = []
    def visit(path):
        if path in seen:
            return
        if not path.exists():
            missing.append(str(path)); return
        seen.add(path)
        text = re.sub(r'(?<!\\)%.*','',path.read_text(encoding='utf-8'))
        for name in re.findall(r'\\input\{([^}]+)\}',text):
            if name == 'build/revision.tex' and not (root/name).exists():
                continue  # explicitly guarded by IfFileExists
            p = root/name
            visit(p if p.suffix else p.with_suffix('.tex'))
    visit(root/'main.tex')
    text = '\n'.join(p.read_text(encoding='utf-8') for p in seen)
    bibs = [root/(name+'.bib') for group in re.findall(r'\\bibliography\{([^}]+)\}',text) for name in group.split(',')]
    keys = set()
    for bib in bibs:
        if not bib.exists(): missing.append(str(bib)); continue
        keys.update(re.findall(r'@\w+\s*\{\s*([^,]+),',bib.read_text(encoding='utf-8')))
    citations = {k.strip() for group in re.findall(r'\\cite\w*\{([^}]+)\}',text) for k in group.split(',')}
    labels = re.findall(r'\\label\{([^}]+)\}',text)
    references = set(re.findall(r'\\(?:eqref|ref|pageref)\{([^}]+)\}',text))
    figure_paths = []
    for name in re.findall(r'\\includegraphics(?:\[[^]]*\])?\{([^}]+)\}',text):
        candidates = [root/name,root/'figures'/name]
        candidates += [p.with_suffix(ext) for p in list(candidates) if not p.suffix for ext in ('.pdf','.png')]
        match = next((p for p in candidates if p.exists()),None)
        if match is None: missing.append(name)
        else: figure_paths.append(match)
    stale = [line for line in text.splitlines() if re.search(r'engineering (?:studies|results).*pending|engineering simulations have not been run',line,re.I)]
    checks = dict(missing_files=missing,missing_citations=sorted(citations-keys),
                  missing_labels=sorted(references-set(labels)),
                  duplicate_labels=sorted({x for x in labels if labels.count(x)>1}),
                  stale_engineering_claims=stale,
                  included_tex_files=len(seen),included_figures=len(figure_paths),
                  checked_citations=len(citations),
                  latex_compiled=False,scope='Static dependency checks; final layout requires Overleaf compilation',
                  contribution_percentage_todo_present='TEAM TODO BEFORE SUBMISSION' in text)
    assert not any(checks[k] for k in ('missing_files','missing_citations','missing_labels','duplicate_labels','stale_engineering_claims')),checks
    with zipfile.ZipFile('report/Overleaf_submission.zip','w',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(seen|set(bibs)|set(figure_paths)):
            z.write(p,p.relative_to(root).as_posix())
    checks['archive']='report/Overleaf_submission.zip'
    Path('docs/pilot_validation/report_checks.json').write_text(json.dumps(checks,indent=2)+'\n')
    print(json.dumps(checks,indent=2))


if __name__ == '__main__':
    main()
