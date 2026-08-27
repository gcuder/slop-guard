"""Reject functions with identical bodies."""

from __future__ import annotations

import ast

from ...diagnostics import Diagnostic
from ...rule import Rule

DEFAULT_MIN_STATEMENTS = 3


class NoDuplicateCode(Rule):
    name = "no-duplicate-code"
    group = "smells"
    reference = "https://refactoring.guru/smells/duplicate-code"
    description = (
        "Disallow two functions in a module with identical bodies of `min_statements` statements "
        "or more, 3 by default."
    )

    def run(self) -> list[Diagnostic]:
        minimum = self.threshold("min_statements", DEFAULT_MIN_STATEMENTS)
        seen: dict[str, str] = {}
        for node in ast.walk(self.source.tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            body = [statement for statement in node.body if not self._is_docstring(statement)]
            if len(body) < minimum:
                continue
            fingerprint = "".join(ast.dump(statement, annotate_fields=False) for statement in body)
            earlier = seen.get(fingerprint)
            if earlier is None:
                seen[fingerprint] = node.name
                continue
            self.report(
                node,
                f"`{node.name}` has the same body as `{earlier}`, so a fix to one has to be "
                f"remembered for the other. Keep one copy and call it from both.",
            )
        return self.diagnostics

    @staticmethod
    def _is_docstring(statement: ast.stmt) -> bool:
        return (
            isinstance(statement, ast.Expr)
            and isinstance(statement.value, ast.Constant)
            and isinstance(statement.value.value, str)
        )
