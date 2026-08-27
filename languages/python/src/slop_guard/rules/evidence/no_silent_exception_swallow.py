"""Reject handlers that discard an exception without acting on it."""

from __future__ import annotations

import ast

from ...rule import Rule


class NoSilentExceptionSwallow(Rule):
    name = "no-silent-exception-swallow"
    group = "evidence"
    description = (
        "Disallow handlers that discard the exception; handle the failure or let it travel. Bare "
        "`except` clauses are covered by no-bare-except."
    )

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        if self._is_silent(node.body):
            caught = self.unparse(node.type) if node.type is not None else "everything"
            self.report(
                node,
                f"This handler catches `{caught}` and discards it, so a failure here is invisible. "
                f"Recover from it, record it with the original cause, or let it propagate.",
            )
        self.generic_visit(node)

    @staticmethod
    def _is_silent(body: list[ast.stmt]) -> bool:
        if len(body) != 1:
            return False
        statement = body[0]
        if isinstance(statement, ast.Pass):
            return True
        return (
            isinstance(statement, ast.Expr)
            and isinstance(statement.value, ast.Constant)
            and statement.value.value is Ellipsis
        )
