"""Every rule shipped with slop-guard, organised into selectable groups."""

from __future__ import annotations

from ..rule import Rule
from . import correctness, evidence, maintainability, performance, readability, security, smells

GROUPS = {
    "evidence": evidence.RULES,
    "correctness": correctness.RULES,
    "maintainability": maintainability.RULES,
    "readability": readability.RULES,
    "security": security.RULES,
    "performance": performance.RULES,
    "smells": smells.RULES,
}

# Groups that a run skips unless it asks for them by name, for rules tied to one framework.
OPT_IN_GROUPS: frozenset[str] = frozenset()

ALL_RULES: tuple[type[Rule], ...] = tuple(
    rule for rules in GROUPS.values() for rule in rules
)

__all__ = ["ALL_RULES", "GROUPS", "OPT_IN_GROUPS"]
