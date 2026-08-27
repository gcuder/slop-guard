"""slop-guard: opinionated checks that reject low-evidence Python."""

from __future__ import annotations

from .diagnostics import Diagnostic
from .registry import RULES, check_file, check_source, rule_names, selected_rules
from .rule import Rule
from .source import SourceFile

__all__ = [
    "Diagnostic",
    "RULES",
    "Rule",
    "SourceFile",
    "check_file",
    "check_source",
    "rule_names",
    "selected_rules",
]
__version__ = "0.1.0"
