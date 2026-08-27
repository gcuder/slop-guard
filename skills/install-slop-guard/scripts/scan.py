#!/usr/bin/env python3
"""Scan a repository with the bundled rules, changing nothing in it.

Mirrors scripts/scan.mjs: either runner scans every detected language, delegating the one it cannot
run itself to the other runtime. The Python rules run in this process; the TypeScript rules are an
Oxlint plugin, so they run through the Node runner, which prepares a cached copy of the linter on
first use.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from detect import SKILL_ROOT, detect, language  # noqa: E402 - needs the path above

ASSETS = SKILL_ROOT / "assets"


def scan_python(paths: list[str], passthrough: list[str]) -> int:
    """Run the bundled Python checker in this process."""
    if not (ASSETS / "python").is_dir():
        print(f"This skill has no bundled Python checker at {ASSETS / 'python'}.", file=sys.stderr)
        return 2
    sys.path.insert(0, str(ASSETS))
    from python.cli import main as check  # noqa: PLC0415 - importable only after the path above

    return check([*passthrough, *paths])


def scan_typescript(paths: list[str], passthrough: list[str]) -> int:
    """Hand the TypeScript rules to the Node runner, which owns the linter cache."""
    if shutil.which("node") is None:
        print(
            "Could not run the TypeScript rules: they are an Oxlint plugin and need Node on PATH.",
            file=sys.stderr,
        )
        return 2
    runner = SKILL_ROOT / "scripts" / "scan.mjs"
    result = subprocess.run(
        ["node", str(runner), "--language", "typescript", *passthrough, *paths],
        check=False,
    )
    return result.returncode


def parse(argv: list[str]) -> tuple[str | None, list[str], list[str]]:
    chosen: str | None = None
    paths: list[str] = []
    passthrough: list[str] = []
    index = 0
    while index < len(argv):
        argument = argv[index]
        if argument == "--language":
            index += 1
            chosen = argv[index] if index < len(argv) else None
        elif argument.startswith("--"):
            passthrough.append(argument)
            following = argv[index + 1] if index + 1 < len(argv) else ""
            if argument in {"--select", "--ignore", "--format"} and following and not following.startswith("--"):
                index += 1
                passthrough.append(following)
        else:
            paths.append(argument)
        index += 1
    return chosen, paths or ["."], passthrough


def main(argv: list[str] | None = None) -> int:
    chosen, paths, passthrough = parse(list(argv if argv is not None else sys.argv[1:]))
    try:
        languages = [language(chosen)] if chosen else [item.language for item in detect(Path.cwd())]
    except KeyError as error:
        print(str(error), file=sys.stderr)
        return 2

    if not languages:
        print(
            "No supported language detected here. Run install.py --list to see what this skill covers.",
            file=sys.stderr,
        )
        return 1

    status = 0
    for entry in languages:
        if len(languages) > 1 or chosen is None:
            print(f"\n== {entry['name']} ==", file=sys.stderr)
        code = scan_python(paths, passthrough) if entry["id"] == "python" else scan_typescript(paths, passthrough)
        status = max(status, code)
    return status


if __name__ == "__main__":
    raise SystemExit(main())
