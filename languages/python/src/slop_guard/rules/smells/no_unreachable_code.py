"""Reject statements that can never run."""

from __future__ import annotations

import ast

from ...rule import Rule

TERMINATORS = (ast.Return, ast.Raise, ast.Break, ast.Continue)


class NoUnreachableCode(Rule):
    name = "no-unreachable-code"
    group = "smells"
    reference = "https://refactoring.guru/smells/dead-code"
    description = "Disallow statements after `return`, `raise`, `break`, or `continue` in the same block."

    def visit_Module(self, node: ast.Module) -> None:
        self._scan(node.body)
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._scan(node.body)
        self.generic_visit(node)

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_For(self, node: ast.For) -> None:
        self._scan(node.body)
        self._scan(node.orelse)
        self.generic_visit(node)

    visit_AsyncFor = visit_For
    visit_While = visit_For
    visit_If = visit_For

    def visit_With(self, node: ast.With) -> None:
        self._scan(node.body)
        self.generic_visit(node)

    visit_AsyncWith = visit_With

    def visit_Try(self, node: ast.Try) -> None:
        self._scan(node.body)
        self._scan(node.orelse)
        self._scan(node.finalbody)
        for handler in node.handlers:
            self._scan(handler.body)
        self.generic_visit(node)

    def _scan(self, body: list[ast.stmt]) -> None:
        for index, statement in enumerate(body[:-1]):
            if isinstance(statement, TERMINATORS):
                following = body[index + 1]
                keyword = type(statement).__name__.lower()
                self.report(
                    following,
                    f"Nothing after the `{keyword}` above can run, so this code is dead. Delete "
                    f"it, or move the `{keyword}` if the order is wrong.",
                )
                return
