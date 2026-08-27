"""Reject comparing `type(...)` values."""

from __future__ import annotations

import ast

from ...rule import Rule


class NoTypeComparison(Rule):
    name = "no-type-comparison"
    group = "readability"
    reference = "https://docs.quantifiedcode.com/python-anti-patterns/readability/do_not_compare_types_use_isinstance.html"
    description = "Disallow `type(a) == type(b)`; it ignores subclasses and reads as a value test."

    def visit_Compare(self, node: ast.Compare) -> None:
        operands = [node.left, *node.comparators]
        if any(isinstance(operator, (ast.Eq, ast.NotEq, ast.Is, ast.IsNot)) for operator in node.ops):
            if any(self._is_type_call(operand) for operand in operands):
                self.report(
                    node,
                    "Comparing `type(...)` asks for an exact class and answers `False` for every "
                    "subclass. Parse the value at its boundary, or use `isinstance` when a class "
                    "check is genuinely what you need.",
                )
        self.generic_visit(node)

    @staticmethod
    def _is_type_call(node: ast.expr) -> bool:
        return (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "type"
            and len(node.args) == 1
        )
