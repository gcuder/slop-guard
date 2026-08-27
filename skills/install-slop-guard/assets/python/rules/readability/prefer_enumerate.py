"""Prefer `enumerate` to walking an index by hand."""

from __future__ import annotations

import ast

from ...rule import Rule


class PreferEnumerate(Rule):
    name = "prefer-enumerate"
    group = "readability"
    reference = "https://docs.quantifiedcode.com/python-anti-patterns/readability/using_an_unpythonic_loop.html"
    description = "Prefer `for index, item in enumerate(items)` to `for index in range(len(items))`."

    def visit_For(self, node: ast.For) -> None:
        sequence = self._range_len_sequence(node.iter)
        if sequence is not None:
            self.report(
                node,
                f"This loop invents an index so it can read `{sequence}` back out. "
                f"`enumerate({sequence})` hands you the index and the item together.",
            )
        self.generic_visit(node)

    def _range_len_sequence(self, iterator: ast.expr) -> str | None:
        if not isinstance(iterator, ast.Call) or not isinstance(iterator.func, ast.Name):
            return None
        if iterator.func.id != "range":
            return None
        for argument in iterator.args:
            if (
                isinstance(argument, ast.Call)
                and isinstance(argument.func, ast.Name)
                and argument.func.id == "len"
                and argument.args
            ):
                return self.unparse(argument.args[0])
        return None
