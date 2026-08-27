"""Prefer a comprehension to `map` or `filter` with a lambda."""

from __future__ import annotations

import ast

from ...rule import Rule


class PreferComprehensionOverMapFilter(Rule):
    name = "prefer-comprehension-over-map-filter"
    group = "readability"
    reference = "https://docs.quantifiedcode.com/python-anti-patterns/readability/using_map_or_filter_where_list_comprehension_is_possible.html"
    description = "Disallow `map` and `filter` with a lambda; a comprehension reads in one direction."

    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Name) and node.func.id in {"map", "filter"} and node.args:
            if isinstance(node.args[0], ast.Lambda):
                example = (
                    "[expression for item in items]"
                    if node.func.id == "map"
                    else "[item for item in items if condition]"
                )
                self.report(
                    node,
                    f"`{node.func.id}` with a lambda makes the reader unpack a function to see "
                    f"what happens to each item. A comprehension, `{example}`, says it directly.",
                )
        self.generic_visit(node)
