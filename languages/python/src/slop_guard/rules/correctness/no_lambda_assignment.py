"""Reject naming a lambda instead of defining a function."""

from __future__ import annotations

import ast

from ...rule import Rule


class NoLambdaAssignment(Rule):
    name = "no-lambda-assignment"
    group = "correctness"
    reference = "https://docs.quantifiedcode.com/python-anti-patterns/correctness/assigning_a_lambda_to_a_variable.html"
    description = "Disallow assigning a lambda to a name; use `def` so the function has a real name."

    def visit_Assign(self, node: ast.Assign) -> None:
        if isinstance(node.value, ast.Lambda):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    self._report(node, target.id)
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        if isinstance(node.value, ast.Lambda) and isinstance(node.target, ast.Name):
            self._report(node, node.target.id)
        self.generic_visit(node)

    def _report(self, node: ast.stmt, name: str) -> None:
        self.report(
            node,
            f"`{name}` is a lambda bound to a name, so tracebacks and reprs show `<lambda>` "
            f"instead of `{name}`. Define it with `def {name}(...)`.",
        )
