"""
Check for duplicate term IDs within each collection.

The id field references a universe term and does not have to match the
filename, but two files in the same collection must never share the
same id — that causes duplicate rows during esgvoc ingestion.
"""

import json
import os
import sys
from collections import defaultdict
from pathlib import Path


SKIP_DIRS = {".git", ".github", ".idea", ".venv", "_CVs", "_scripts"}


def main():
    repo_root = Path(__file__).parents[1]

    failing = []
    for entry in sorted(os.scandir(repo_root), key=lambda e: e.name):
        if not entry.is_dir() or entry.name in SKIP_DIRS or entry.name.startswith("."):
            continue

        ids_seen: dict[str, list[str]] = defaultdict(list)
        for cv_file in sorted(Path(entry.path).glob("*.json")):
            with open(cv_file) as fh:
                content = json.load(fh)

            if "id" not in content:
                continue

            ids_seen[content["id"]].append(str(cv_file))

        for term_id, files in ids_seen.items():
            if len(files) > 1:
                failing.append(
                    f"{entry.name}: duplicate id '{term_id}' in {files}"
                )

    if failing:
        print("Duplicate term IDs found:", file=sys.stderr)
        for f in failing:
            print(f"  {f}", file=sys.stderr)
        raise SystemExit(1)

    print("No duplicate term IDs found.")


if __name__ == "__main__":
    main()
