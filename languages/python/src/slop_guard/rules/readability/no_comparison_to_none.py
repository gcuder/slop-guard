"""Reject `== None`."""

from __future__ import annotations

import ast

from ...rule import Rule


class NoComparisonToNone(Rule):
    name = "no-comparison-to-none"
    group = "readability"
    reference = "https://docs.quantifiedcode.com/python-anti-patterns/readability/comparison_to_none.html"
    description = "Disallow `== None` and `!= None`; `None` is a singleton, so compare with `is`."

    def visit_Compare(self, node: ast.Compare) -> None:
        for operator, comparator in zip(node.ops, node.comparators):
            if isinstance(operator, (ast.Eq, ast.NotEq)) and self._is_none(comparator):
                replacement = "is" if isinstance(operator, ast.Eq) else "is not"
                self.report(
                    node,
                    f"`None` is a singleton, so compare identity: write `{replacement} None`. "
                    f"`==` calls `__eq__`, which an object can define to answer anything.",
                )
            elif isinstance(operator, (ast.Eq, ast.NotEq)) and self._is_none(node.left):
                self.report(
                    node,
                    "`None` is a singleton, so compare identity with `is` rather than `==`.",
                )
        self.generic_visit(node)

    @staticmethod
    def _is_none(node: ast.expr) -> bool:
        return isinstance(node, ast.Constant) and node.value is None
