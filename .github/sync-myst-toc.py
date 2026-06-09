#!/usr/bin/env python3
"""
Sync myst.yml TOC with DATA 88C lab and lecture notebooks on disk.

Labs:   lab/N/labNN/labNN.ipynb
Lectures: lec/N/lecNN.ipynb

Run from repository root. Exits 0 if no change, 2 on error.
"""
import json
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("PyYAML required: pip install pyyaml", file=sys.stderr)
    sys.exit(2)

REPO_ROOT = Path(__file__).resolve().parent.parent
MYST_PATH = REPO_ROOT / "myst.yml"

EXIT_SUCCESS = 0
EXIT_ERROR = 2

PART_TITLES = {
    "1": "Part 1 - Introduction to Python",
    "2": "Part 2 - Recursion and Object-Oriented Programming",
    "3": "Part 3 - Working with Data Structures",
}

TITLE_PATTERNS = [
    re.compile(r"^##\s+((?:Lab|Lecture)\s+.+)$", re.M),
    re.compile(r"^#\s+((?:Lab|Lecture)\s+.+)$", re.M),
]


def notebook_title(nb_path: Path, default: str) -> str:
    """Read the best lab/lecture heading from a notebook, if present."""
    try:
        with open(nb_path, encoding="utf-8") as f:
            nb = json.load(f)
    except (OSError, json.JSONDecodeError):
        return default

    candidates = []
    for cell in nb.get("cells", []):
        if cell.get("cell_type") != "markdown":
            continue
        src = "".join(cell.get("source", []))
        for pattern in TITLE_PATTERNS:
            match = pattern.search(src)
            if match:
                candidates.append(match.group(1).strip())

    if not candidates:
        return default

    descriptive = [title for title in candidates if ":" in title]
    return descriptive[0] if descriptive else candidates[0]


def find_part_lectures(part: str) -> list[dict]:
    """Find lecNN.ipynb files under lec/part/, sorted by NN."""
    base = REPO_ROOT / "lec" / part
    if not base.is_dir():
        return []

    pattern = re.compile(r"^lec(\d+)\.ipynb$", re.I)
    entries = []
    for path in sorted(base.iterdir()):
        if not path.is_file():
            continue
        match = pattern.match(path.name)
        if not match:
            continue
        num = match.group(1)
        rel = str(path.relative_to(REPO_ROOT)).replace("\\", "/")
        default = f"Lecture {num.zfill(2)}"
        entries.append({"title": notebook_title(path, default), "file": rel})

    entries.sort(key=lambda e: int(re.search(r"lec(\d+)", e["file"], re.I).group(1)))
    return entries


def find_part_labs(part: str) -> list[dict]:
    """Find labNN/labNN.ipynb files under lab/part/, sorted by NN."""
    base = REPO_ROOT / "lab" / part
    if not base.is_dir():
        return []

    pattern = re.compile(r"^lab(\d+)$")
    entries = []
    for path in sorted(base.iterdir()):
        if not path.is_dir():
            continue
        match = pattern.match(path.name)
        if not match:
            continue
        num = match.group(1)
        nb = path / f"{path.name}.ipynb"
        if not nb.is_file():
            continue
        rel = str(nb.relative_to(REPO_ROOT)).replace("\\", "/")
        default = f"Lab {num.zfill(2)}"
        entries.append({"title": notebook_title(nb, default), "file": rel})

    entries.sort(key=lambda e: int(re.search(r"lab(\d+)", e["file"]).group(1)))
    return entries


def build_toc() -> list[dict]:
    toc = []

    intro = REPO_ROOT / "intro.md"
    if intro.exists():
        toc.append({"file": "intro.md"})

    for part in sorted(PART_TITLES):
        children = []
        lectures = find_part_lectures(part)
        labs = find_part_labs(part)
        if lectures:
            children.append({"title": "Lectures", "children": lectures})
        if labs:
            children.append({"title": "Labs", "children": labs})
        if children:
            toc.append({"title": PART_TITLES[part], "children": children})

    return toc


def main() -> int:
    if not MYST_PATH.is_file():
        print(f"Error: {MYST_PATH} not found", file=sys.stderr)
        return EXIT_ERROR

    toc = build_toc()

    try:
        with open(MYST_PATH, encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        print(f"Error: invalid YAML in {MYST_PATH}: {e}", file=sys.stderr)
        return EXIT_ERROR

    if data is None:
        data = {}
    if "project" not in data:
        data["project"] = {}

    old_toc = data["project"].get("toc", [])
    if old_toc == toc:
        return EXIT_SUCCESS

    data["project"]["toc"] = toc
    with open(MYST_PATH, "w", encoding="utf-8") as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    return EXIT_SUCCESS


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(EXIT_ERROR)
