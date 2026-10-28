"""Keep the plugin version identical everywhere it is stated. Usage: versions.py check | bump X.Y.Z"""

import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
MANIFEST = ROOT / ".claude-plugin" / "plugin.json"
LINE = re.compile(r"^Plugin version: (\d+\.\d+\.\d+)\.", re.M)


def stated_files():
    files = [ROOT / "LAWS.md", ROOT / "QUALITY.md"]
    files += sorted((ROOT / "agents").glob("*.md"))
    files += sorted((ROOT / "skills").glob("*/SKILL.md"))
    return files


def manifest_version():
    return json.loads(MANIFEST.read_text())["version"]


def mismatches(expected):
    found = {}
    for path in stated_files():
        match = LINE.search(path.read_text())
        found[path] = match.group(1) if match else None
    return {p: v for p, v in found.items() if v != expected}


def check():
    expected = manifest_version()
    bad = mismatches(expected)
    for path, version in bad.items():
        print(f"{path.relative_to(ROOT)}: {version or 'missing'} (expected {expected})")
    return 1 if bad else 0


def bump(new):
    if not re.fullmatch(r"\d+\.\d+\.\d+", new):
        print("version must be X.Y.Z")
        return 1
    data = json.loads(MANIFEST.read_text())
    data["version"] = new
    MANIFEST.write_text(json.dumps(data, indent=2) + "\n")
    for path in stated_files():
        path.write_text(LINE.sub(f"Plugin version: {new}.", path.read_text()))
    return check()


def main(argv):
    if argv[1:2] == ["check"]:
        return check()
    if argv[1:2] == ["bump"] and len(argv) == 3:
        return bump(argv[2])
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
