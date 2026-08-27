"""Reject `Any` inputs except the explicit `cause` convention."""

from __future__ import annotations

import ast

from ...rule import FunctionNode, Rule

ALLOWED_NAMES = frozenset({"cause"})


class NoAnyParameters(Rule):
    name = "no-any-parameters"
    group = "evidence"
    description = (
        "Disallow `Any` function parameters except `cause`; parse untrusted input at its "
        "I/O boundary instead."
    )

    def visit_FunctionDef(self, node: FunctionNode) -> None:
        self._check(node)
        self.generic_visit(node)

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_Lambda(self, node: ast.Lambda) -> None:
        self.generic_visit(node)

    def _check(self, node: FunctionNode) -> None:
        variadic = self.variadic_parameters(node) if self.flag("allow_variadic_any") else set()
        for parameter in self.parameters(node):
            if parameter.arg in ALLOWED_NAMES or parameter.arg in variadic:
                continue
            if not self.is_any(parameter.annotation):
                continue
            self.report(
                parameter.annotation or parameter,
                f"Parameter `{parameter.arg}` leaves input unparsed. Accept a named domain type "
                f"and validate the payload at the I/O boundary before calling this function.",
            )
