"""Command line entry point for slop-guard."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from .config import Config, find_pyproject
from .diagnostics import Diagnostic
from .registry import RULES, check_file, group_names, rule_names, selected_rules


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="slop-guard",
        description="Reject low-evidence Python patterns.",
    )
    parser.add_argument("paths", nargs="*", default=["."], help="Files or directories to check.")
    parser.add_argument("--config", type=Path, help="Path to a pyproject.toml holding [tool.slop-guard].")
    parser.add_argument(
        "--select",
        help="Comma-separated rule names or group:<name> tokens to run instead of the defaults.",
    )
    parser.add_argument("--ignore", help="Comma-separated rule names or group:<name> tokens to skip.")
    parser.add_argument("--format", choices=("text", "json"), default="text", help="Output format.")
    parser.add_argument("--exit-zero", action="store_true", help="Always exit 0, even with findings.")
    parser.add_argument("--list-rules", action="store_true", help="Print every rule and exit.")
    return parser


def collect_files(paths: Sequence[str], exclude: Sequence[str]) -> list[Path]:
    """Expand the requested paths into Python files, skipping excluded directories."""
    excluded = set(exclude)
    found: list[Path] = []
    for entry in paths:
        path = Path(entry)
        if path.is_file():
            found.append(path)
            continue
        for candidate in sorted(path.rglob("*.py")):
            if excluded.isdisjoint(candidate.parts):
                found.append(candidate)
    return found


def print_rules() -> None:
    """List every rule, grouped, with the source of the pattern it enforces."""
    for group in group_names():
        members = [name for name in rule_names() if RULES[name].group == group]
        print(f"[{group}] {len(members)} rule(s)")
        for name in members:
            rule = RULES[name]
            reference = f"  see {rule.reference}" if rule.reference else ""
            print(f"  {name}: {rule.description}{reference}")


def report(findings: Sequence[Diagnostic], style: str, rules: int) -> None:
    """Print the findings in the requested format."""
    if style == "json":
        print(json.dumps([finding.as_dict() for finding in findings], indent=2))
        return
    for finding in findings:
        print(finding.render())
    print(f"{len(findings)} finding(s) across {rules} rule(s).", file=sys.stderr)


def collect_findings(
    paths: Sequence[str], config: Config, rules: Sequence[type]
) -> tuple[list[Diagnostic], int]:
    """Check every requested file, counting the ones that could not be parsed."""
    findings: list[Diagnostic] = []
    failures = 0
    for path in collect_files(paths, config.exclude):
        try:
            findings.extend(check_file(path, rules, config.rules))
        except SyntaxError as error:
            failures += 1
            print(f"{path}: could not parse ({error.msg})", file=sys.stderr)
    return findings, failures


def main(argv: Sequence[str] | None = None) -> int:
    arguments = build_parser().parse_args(argv)

    if arguments.list_rules:
        print_rules()
        return 0

    paths = arguments.paths or ["."]
    config = Config.load(arguments.config or find_pyproject(Path(paths[0])))
    select = _split(arguments.select) or config.select
    ignore = _split(arguments.ignore) or config.ignore

    try:
        rules = selected_rules(select, ignore)
    except KeyError as error:
        print(str(error), file=sys.stderr)
        return 2

    findings, failures = collect_findings(paths, config, rules)
    report(findings, arguments.format, len(rules))

    if arguments.exit_zero:
        return 0
    return 1 if findings or failures else 0


def _split(value: str | None) -> tuple[str, ...] | None:
    if not value:
        return None
    return tuple(item.strip() for item in value.split(",") if item.strip())
