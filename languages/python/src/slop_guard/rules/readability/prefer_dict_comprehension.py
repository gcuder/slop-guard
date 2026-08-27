"""Prefer a dict comprehension to `dict()` around a generator."""

from __future__ import annotations

import ast

from ...rule import Rule


class PreferDictComprehension(Rule):
    name = "prefer-dict-comprehension"
    group = "readability"
    reference = "https://docs.quantifiedcode.com/python-anti-patterns/readability/not_using_a_dict_comprehension.html"
    description = "Prefer `{key: value for ...}` to `dict((key, value) for ...)`."

    def visit_Call(self, node: ast.Call) -> None:
        if (
            isinstance(node.func, ast.Name)
            and node.func.id == "dict"
            and len(node.args) == 1
            and not node.keywords
            and isinstance(node.args[0], (ast.GeneratorExp, ast.ListComp))
        ):
            self.report(
                node,
                "This builds pairs and then hands them to `dict()`. A dict comprehension, "
                "`{key: value for ...}`, says the same thing in one step and skips the "
                "intermediate tuples.",
            )
        self.generic_visit(node)
