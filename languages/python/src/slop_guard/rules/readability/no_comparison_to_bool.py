"""Reject `== True` and `== False`."""

from __future__ import annotations

import ast

from ...rule import Rule


class NoComparisonToBool(Rule):
    name = "no-comparison-to-bool"
    group = "readability"
    reference = "https://docs.quantifiedcode.com/python-anti-patterns/readability/comparison_to_true.html"
    description = (
        "Disallow `== True` and `== False`; test the value itself. `is True` is left alone, since it "
        "is the only way to tell `True` from `1`."
    )

    def visit_Compare(self, node: ast.Compare) -> None:
        for operator, comparator in zip(node.ops, node.comparators):
            if isinstance(operator, (ast.Eq, ast.NotEq)) and self._is_bool(comparator):
                value = comparator.value
                subject = self.unparse(node.left)
                negated = isinstance(operator, ast.NotEq) != (value is False)
                fix = f"if {subject}" if negated else f"if not {subject}"
                self.report(
                    node,
                    f"Comparing to `{value}` adds a step without adding a decision. Write "
                    f"`{fix}`.",
                )
        self.generic_visit(node)

    @staticmethod
    def _is_bool(node: ast.expr) -> bool:
        return isinstance(node, ast.Constant) and isinstance(node.value, bool)
