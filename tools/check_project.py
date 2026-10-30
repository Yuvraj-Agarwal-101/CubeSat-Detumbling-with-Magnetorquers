"""Run available correctness checks and record reproducible report evidence.

This command does not run an engineering simulation or replace the future
run_all.py study pipeline owned by Person 4.
"""

import json
from pathlib import Path
import platform
import subprocess
import sys
import xml.etree.ElementTree as ET

from src.config import case_summary, load_config


ROOT = Path(__file__).resolve().parents[1]


def main():
    build = ROOT / "report/build"
    build.mkdir(parents=True, exist_ok=True)
    case = load_config()
    subprocess.run([sys.executable, "-m", "pytest", "-q", "--junitxml", str(build / "pytest.xml")],
                   cwd=ROOT, check=True)
    suites = list(ET.parse(build / "pytest.xml").getroot().iter("testsuite"))
    counts = {key: sum(int(s.attrib.get(key, 0)) for s in suites)
              for key in ("tests", "failures", "errors", "skipped")}
    revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    dirty = bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True).strip())
    summary = {"revision": revision, "working_tree_modified": dirty,
               "python_version": platform.python_version(), "counts": counts,
               "case": case_summary(case),
               "scope": "Physics, inputs, numerical method and exact convergence tests. No magnetic detumbling simulation."}
    (build / "verification.json").write_text(json.dumps(summary, indent=2, allow_nan=False) + "\n", encoding="utf8")
    revision_tex = r"\texttt{" + revision + "}"
    if dirty:
        revision_tex += " with local source changes"
    (build / "revision.tex").write_text(revision_tex + "\n", encoding="utf8")
    (build / "test_count.tex").write_text(str(counts["tests"]) + "\n", encoding="utf8")
    print("Recorded report/build/verification.json and current revision evidence")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
