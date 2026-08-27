"""Reject conditional spreads that use an empty dict to omit fields."""

from __future__ import annotations

import ast

from ...rule import Rule


class NoConditionalEmptyDictSpread(Rule):
    name = "no-conditional-empty-dict-spread"
    group = "evidence"
    description = "Disallow `{**(payload if cond else {})}`; declare the optional field explicitly."

    def visit_Dict(self, node: ast.Dict) -> None:
        for key, value in zip(node.keys, node.values):
            if key is None and self._is_empty_branch(value):
                self.report(
                    value,
                    "This spread makes a key exist only sometimes, so the resulting type is a "
                    "guess. Declare the field and set it to a documented default, or build the "
                    "payload with a named function.",
                )
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Name) and node.func.id == "dict":
            for keyword in node.keywords:
                if keyword.arg is None and self._is_empty_branch(keyword.value):
                    self.report(
                        keyword.value,
                        "This spread makes a key exist only sometimes, so the resulting type is a "
                        "guess. Declare the field and set it to a documented default.",
                    )
        self.generic_visit(node)

    @staticmethod
    def _is_empty_branch(value: ast.expr) -> bool:
        if not isinstance(value, ast.IfExp):
            return False
        return any(
            isinstance(branch, ast.Dict) and not branch.keys
            for branch in (value.body, value.orelse)
        )
