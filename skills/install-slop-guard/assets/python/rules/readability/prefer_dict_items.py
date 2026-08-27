"""Prefer `items()` to looking each key up inside the loop."""

from __future__ import annotations

import ast

from ...rule import Rule


class PreferDictItems(Rule):
    name = "prefer-dict-items"
    group = "readability"
    reference = "https://docs.quantifiedcode.com/python-anti-patterns/readability/not_using_items_to_iterate_over_a_dictionary.html"
    description = "Prefer `for key, value in mapping.items()` to looking the key up in the body."

    def visit_For(self, node: ast.For) -> None:
        if isinstance(node.iter, ast.Name) and isinstance(node.target, ast.Name):
            mapping = node.iter.id
            key = node.target.id
            if self._looks_up_key(node.body, mapping, key):
                self.report(
                    node,
                    f"The body looks `{key}` up in `{mapping}` on every pass, which the loop "
                    f"can hand you directly. Write `for {key}, value in {mapping}.items():`.",
                )
        self.generic_visit(node)

    @staticmethod
    def _looks_up_key(body: list[ast.stmt], mapping: str, key: str) -> bool:
        for statement in body:
            for node in ast.walk(statement):
                if (
                    isinstance(node, ast.Subscript)
                    and isinstance(node.value, ast.Name)
                    and node.value.id == mapping
                    and isinstance(node.slice, ast.Name)
                    and node.slice.id == key
                ):
                    return True
        return False
