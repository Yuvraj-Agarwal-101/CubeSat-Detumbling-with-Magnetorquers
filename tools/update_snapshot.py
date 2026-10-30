"""Record hashes of indexed project files, excluding the checksum file itself."""

import hashlib
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[1]


def main():
    names = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT).decode().split("\0")
    lines = []
    for name in sorted(set(names)):
        if not name or name == "SHA256SUMS.txt":
            continue
        path = ROOT / name
        if path.is_file():
            lines.append(hashlib.sha256(path.read_bytes()).hexdigest() + "  " + name)
    (ROOT / "SHA256SUMS.txt").write_text("\n".join(lines) + "\n", encoding="utf8")


if __name__ == "__main__":
    main()
