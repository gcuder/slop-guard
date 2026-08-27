"""Prefer tuple assignment to a temporary variable when updating two names."""

from __future__ import annotations

import ast

from ...rule import Rule


class PreferTupleSwap(Rule):
    name = "prefer-tuple-swap"
    group = "readability"
    reference = "https://docs.quantifiedcode.com/python-anti-patterns/readability/not_using_unpacking_for_updating_multiple_values_at_once.html"
    description = "Prefer `first, second = second, new_value` to shuffling through a temporary."

    def visit_Module(self, node: ast.Module) -> None:
        self._scan(node.body)
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._scan(node.body)
        self.generic_visit(node)

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_While(self, node: ast.While) -> None:
        self._scan(node.body)
        self.generic_visit(node)

    def visit_For(self, node: ast.For) -> None:
        self._scan(node.body)
        self.generic_visit(node)

    def _scan(self, body: list[ast.stmt]) -> None:
        for index in range(len(body) - 2):
            first, second, third = body[index], body[index + 1], body[index + 2]
            temporary = self._simple_assignment(first)
            middle = self._simple_assignment(second)
            last = self._simple_assignment(third)
            if temporary is None or middle is None or last is None:
                continue
            temporary_name, source = temporary
            updated, _ = middle
            restored, restored_source = last
            if source == updated and restored_source == temporary_name and restored != temporary_name:
                self.report(
                    first,
                    f"`{temporary_name}` exists only to carry `{source}` across the next "
                    f"assignment. Update both names at once: "
                    f"`{restored}, {updated} = {self.unparse(second.value)}, ...` reads as one step.",
                )

    def _simple_assignment(self, statement: ast.stmt) -> tuple[str, str] | None:
        if (
            isinstance(statement, ast.Assign)
            and len(statement.targets) == 1
            and isinstance(statement.targets[0], ast.Name)
        ):
            return statement.targets[0].id, self.unparse(statement.value)
        return None
