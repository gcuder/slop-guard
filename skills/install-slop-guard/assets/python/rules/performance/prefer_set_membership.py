"""Prefer a set over a list for membership tests."""

from __future__ import annotations

import ast

from ...rule import Rule


class PreferSetMembership(Rule):
    name = "prefer-set-membership"
    group = "performance"
    reference = "https://docs.quantifiedcode.com/python-anti-patterns/performance/using_key_in_list_to_check_if_key_is_contained_in_a_list.html"
    description = "Prefer `value in {...}` to `value in [...]`; a list membership test is linear."

    def visit_Compare(self, node: ast.Compare) -> None:
        for operator, comparator in zip(node.ops, node.comparators):
            if isinstance(operator, (ast.In, ast.NotIn)) and isinstance(comparator, (ast.List, ast.Tuple)):
                if len(comparator.elts) > 1 and all(
                    isinstance(element, ast.Constant) for element in comparator.elts
                ):
                    self.report(
                        node,
                        f"Testing membership against a {type(comparator).__name__.lower()} scans it "
                        f"element by element. Write the literal as a set so the test is a hash "
                        f"lookup.",
                    )
        self.generic_visit(node)
