"""Require boundary parsing instead of ad hoc runtime type checks."""

from __future__ import annotations

import ast
from typing import Mapping

from ...rule import TYPE_GUARD_PATHS, FunctionNode, Rule
from ...source import SourceFile


class NoRuntimeIsinstance(Rule):
    name = "no-runtime-isinstance"
    group = "evidence"
    description = (
        "Disallow ad hoc `isinstance` narrowing; parse values at the boundary and keep the parsed "
        "type. `type(...)` comparisons are covered by no-type-comparison."
    )

    def __init__(self, source: SourceFile, options: Mapping[str, object] | None = None) -> None:
        super().__init__(source, options)
        self._guard_depth = 0

    def visit_FunctionDef(self, node: FunctionNode) -> None:
        is_guard = self.flag("allow_in_type_guards") and self._is_type_guard(node)
        self._guard_depth += 1 if is_guard else 0
        self.generic_visit(node)
        self._guard_depth -= 1 if is_guard else 0

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_Call(self, node: ast.Call) -> None:
        if self._guard_depth == 0 and isinstance(node.func, ast.Name) and node.func.id == "isinstance":
            subject = self.unparse(node.args[0]) if node.args else "the value"
            self.report(
                node,
                f"`isinstance` narrows `{subject}` by inspection rather than by contract. Parse the "
                f"value where it enters the program and pass the parsed type onward.",
            )
        self.generic_visit(node)

    def _is_type_guard(self, node: FunctionNode) -> bool:
        returns = node.returns
        if returns is None:
            return False
        return self.imports.matches(returns, *TYPE_GUARD_PATHS)
