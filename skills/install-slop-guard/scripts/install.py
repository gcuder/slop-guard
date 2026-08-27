"""Detect which languages a repository contains and vendor the matching slop-guard rules.

Mirrors scripts/install.mjs; both read languages.json through detect.py, so adding a language
changes neither.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from detect import REGISTRY, SKILL_ROOT, Detection, detect, language  # noqa: E402 - needs the path above


def check_destination(language: dict, target: Path, force: bool) -> None:
    """Fail before any copy happens, so a conflict never half-installs a repository."""
    source = SKILL_ROOT / "assets" / language["assets"]
    if not source.is_dir():
        raise SystemExit(f"This skill has no bundled assets for {language['id']}.")
    if target.exists() and not force:
        raise SystemExit(
            f"Refusing to overwrite {target}. Re-run with --force only after reviewing the "
            f"existing files."
        )


def install(language: dict, target: Path) -> None:
    source = SKILL_ROOT / "assets" / language["assets"]
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(source, target, ignore=shutil.ignore_patterns("__pycache__"))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Vendor slop-guard rules for the detected languages.")
    parser.add_argument("target", nargs="?", help="Destination directory for a single language.")
    parser.add_argument("--language", help="Install one language instead of every detected one.")
    parser.add_argument("--target", dest="target_option", help="Destination directory.")
    parser.add_argument("--force", action="store_true", help="Replace an existing destination.")
    parser.add_argument("--detect", action="store_true", help="Report detected languages and exit.")
    parser.add_argument("--list", action="store_true", help="List supported languages and exit.")
    parser.add_argument("--json", action="store_true", help="Print detection output as JSON.")
    return parser


def main() -> int:
    arguments = build_parser().parse_args()
    root = Path.cwd()
    target_argument = arguments.target_option or arguments.target

    if arguments.list:
        for language in REGISTRY["languages"]:
            print(f"{language['id']}\t{language['name']}\t{language['host']}\t{language['reference']}")
        return 0

    chosen = detect(root)
    if arguments.language:
        try:
            chosen = [Detection(language=language(arguments.language), markers=(), sources=0)]
        except KeyError as error:
            print(str(error), file=sys.stderr)
            return 1

    if not chosen:
        print("No supported language detected. Run with --list to see what this skill covers.", file=sys.stderr)
        return 1

    if arguments.detect:
        report = [
            {
                "id": result.language["id"],
                "name": result.language["name"],
                "reference": result.language["reference"],
                "target": result.language["target"],
                "markers": list(result.markers),
                "sourceFiles": result.sources,
            }
            for result in chosen
        ]
        if arguments.json:
            print(json.dumps(report, indent=2))
        else:
            for entry in report:
                evidence = ", ".join(entry["markers"]) if entry["markers"] else f"{entry['sourceFiles']} source file(s)"
                print(f"{entry['id']}\t{entry['name']}\tdetected via {evidence}\tread {entry['reference']}")
        return 0

    if target_argument and len(chosen) > 1:
        print("--target applies to one language; pass --language as well.", file=sys.stderr)
        return 1

    planned = [
        (result.language, root / (target_argument or result.language["target"])) for result in chosen
    ]
    for language, target in planned:
        check_destination(language, target, arguments.force)

    for language, target in planned:
        install(language, target)
        print(f"Copied the {language['name']} rules to {target}")
        print(f"  entry point: {target / language['entry']}")
        print(f"  next: follow {SKILL_ROOT / language['reference']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
