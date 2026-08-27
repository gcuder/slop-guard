"""Prefer `zip` to indexing two sequences with the same counter."""

from __future__ import annotations

import ast

from ...rule import Rule


class PreferZip(Rule):
    name = "prefer-zip"
    group = "readability"
    reference = "https://docs.quantifiedcode.com/python-anti-patterns/readability/not_using_zip_to_iterate_over_a_pair_of_lists.html"
    description = "Prefer `for left, right in zip(a, b)` to indexing both sequences by a counter."

    def visit_For(self, node: ast.For) -> None:
        counter = self._range_len_counter(node)
        if counter is not None:
            indexed = self._indexed_sequences(node.body, counter)
            if len(indexed) >= 2:
                names = ", ".join(sorted(indexed))
                self.report(
                    node,
                    f"This walks an index so it can read {names} in step. `zip({names})` pairs "
                    f"them directly and stops at the shorter one.",
                )
        self.generic_visit(node)

    @staticmethod
    def _range_len_counter(node: ast.For) -> str | None:
        if not isinstance(node.target, ast.Name) or not isinstance(node.iter, ast.Call):
            return None
        if not isinstance(node.iter.func, ast.Name) or node.iter.func.id != "range":
            return None
        for argument in node.iter.args:
            if (
                isinstance(argument, ast.Call)
                and isinstance(argument.func, ast.Name)
                and argument.func.id == "len"
            ):
                return node.target.id
        return None

    @staticmethod
    def _indexed_sequences(body: list[ast.stmt], counter: str) -> set[str]:
        found: set[str] = set()
        for statement in body:
            for node in ast.walk(statement):
                if (
                    isinstance(node, ast.Subscript)
                    and isinstance(node.value, ast.Name)
                    and isinstance(node.slice, ast.Name)
                    and node.slice.id == counter
                ):
                    found.add(node.value.id)
        return found
