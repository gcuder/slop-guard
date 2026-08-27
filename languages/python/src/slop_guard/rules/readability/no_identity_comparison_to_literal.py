"""Reject `is` against a literal."""

from __future__ import annotations

import ast

from ...rule import Rule


class NoIdentityComparisonToLiteral(Rule):
    name = "no-identity-comparison-to-literal"
    group = "readability"
    reference = "https://docs.quantifiedcode.com/python-anti-patterns/readability/test_for_object_identity_should_be_is_not.html"
    description = "Disallow `is` against a number, string, or container literal; use `==`."

    def visit_Compare(self, node: ast.Compare) -> None:
        for operator, comparator in zip(node.ops, node.comparators):
            if isinstance(operator, (ast.Is, ast.IsNot)) and self._is_literal(comparator):
                replacement = "==" if isinstance(operator, ast.Is) else "!="
                self.report(
                    node,
                    f"`is` asks whether these are the same object, which for a literal depends on "
                    f"how the interpreter happened to cache it. Compare values with "
                    f"`{replacement}`, and keep `is` for `None`.",
                )
        self.generic_visit(node)

    @staticmethod
    def _is_literal(node: ast.expr) -> bool:
        if isinstance(node, (ast.List, ast.Dict, ast.Set, ast.Tuple)):
            return True
        return isinstance(node, ast.Constant) and node.value is not None and not isinstance(node.value, bool)
