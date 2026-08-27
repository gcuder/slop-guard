"""Prefer `mapping.get(key, default)` over an if/else around a lookup."""

from __future__ import annotations

import ast

from ...rule import Rule


class PreferDictGet(Rule):
    name = "prefer-dict-get"
    group = "correctness"
    reference = "https://docs.quantifiedcode.com/python-anti-patterns/correctness/not_using_get_to_return_a_default_value_from_a_dictionary.html"
    description = "Prefer `mapping.get(key, default)` to branching on whether the key is present."

    def visit_If(self, node: ast.If) -> None:
        test = node.test
        if (
            isinstance(test, ast.Compare)
            and len(test.ops) == 1
            and isinstance(test.ops[0], ast.In)
            and isinstance(test.comparators[0], ast.Name)
            and len(node.body) == 1
            and len(node.orelse) == 1
        ):
            mapping = test.comparators[0].id
            key = self.unparse(test.left)
            present, missing = node.body[0], node.orelse[0]
            if self._assigns_lookup(present, mapping, key) and isinstance(missing, ast.Assign):
                default = self.unparse(missing.value)
                self.report(
                    node,
                    f"This branches on whether `{key}` is in `{mapping}` only to pick a default. "
                    f"Write `{mapping}.get({key}, {default})`.",
                )
        self.generic_visit(node)

    def _assigns_lookup(self, statement: ast.stmt, mapping: str, key: str) -> bool:
        return (
            isinstance(statement, ast.Assign)
            and isinstance(statement.value, ast.Subscript)
            and isinstance(statement.value.value, ast.Name)
            and statement.value.value.id == mapping
            and self.unparse(statement.value.slice) == key
        )
