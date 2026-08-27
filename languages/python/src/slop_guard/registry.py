"""The rule registry and the entry point that runs rules over a file."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Mapping, Sequence

from .diagnostics import Diagnostic
from .rule import Rule
from .rules import ALL_RULES, GROUPS, OPT_IN_GROUPS
from .source import SourceFile

RULES: dict[str, type[Rule]] = {rule.name: rule for rule in ALL_RULES}
GROUP_PREFIX = "group:"


def rule_names() -> list[str]:
    return sorted(RULES)


def group_names() -> list[str]:
    return sorted(GROUPS)


def default_rule_names() -> list[str]:
    """Every rule outside an opt-in group, which is what a run checks unless told otherwise."""
    return sorted(
        rule.name for group, rules in GROUPS.items() if group not in OPT_IN_GROUPS for rule in rules
    )


def expand(names: Sequence[str]) -> list[str]:
    """Resolve a mixed list of rule names and `group:<name>` tokens into rule names."""
    resolved: list[str] = []
    unknown: list[str] = []
    for name in names:
        if name.startswith(GROUP_PREFIX):
            group = name[len(GROUP_PREFIX) :]
            if group not in GROUPS:
                unknown.append(name)
                continue
            resolved.extend(rule.name for rule in GROUPS[group])
        elif name in RULES:
            resolved.append(name)
        else:
            unknown.append(name)
    if unknown:
        raise KeyError(f"Unknown rule(s) or group(s): {', '.join(sorted(unknown))}")
    return resolved


def selected_rules(select: Sequence[str] | None, ignore: Sequence[str] | None) -> list[type[Rule]]:
    """Resolve a selection into concrete rule classes."""
    chosen = expand(select) if select else default_rule_names()
    excluded = set(expand(ignore)) if ignore else set()
    seen: set[str] = set()
    ordered: list[str] = []
    for name in chosen:
        if name not in excluded and name not in seen:
            seen.add(name)
            ordered.append(name)
    return [RULES[name] for name in ordered]


def check_source(
    source: SourceFile,
    rules: Iterable[type[Rule]] | None = None,
    options: Mapping[str, Mapping[str, object]] | None = None,
) -> list[Diagnostic]:
    """Run every selected rule over one parsed file."""
    selection = list(rules) if rules is not None else selected_rules(None, None)
    settings = options or {}
    found: list[Diagnostic] = []
    for rule_class in selection:
        found.extend(rule_class(source, settings.get(rule_class.name, {})).run())
    return sorted(found, key=lambda item: (item.line, item.column, item.rule))


def check_file(
    path: Path,
    rules: Iterable[type[Rule]] | None = None,
    options: Mapping[str, Mapping[str, object]] | None = None,
) -> list[Diagnostic]:
    text = path.read_text(encoding="utf-8")
    return check_source(SourceFile.parse(text, path), rules, options)
