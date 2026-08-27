"""Prefer named placeholders over repeated dictionary lookups when formatting."""

from __future__ import annotations

import ast

from ...rule import Rule

MINIMUM_LOOKUPS = 2


class PreferFormatMapping(Rule):
    name = "prefer-format-mapping"
    group = "readability"
    reference = "https://docs.quantifiedcode.com/python-anti-patterns/readability/not_using_dict_keys_when_formatting_strings.html"
    description = "Prefer `\"{key}\".format(**mapping)` to passing `mapping[\"key\"]` several times."

    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Attribute) and node.func.attr == "format":
            owners = [self._mapping_name(argument) for argument in node.args]
            named = [owner for owner in owners if owner is not None]
            if len(named) >= MINIMUM_LOOKUPS and len(set(named)) == 1:
                mapping = named[0]
                self.report(
                    node,
                    f"Every argument here is a lookup in `{mapping}`, so the format string and the "
                    f"argument list have to be kept in step. Name the keys in the string and pass "
                    f"`**{mapping}`.",
                )
        self.generic_visit(node)

    @staticmethod
    def _mapping_name(argument: ast.expr) -> str | None:
        if (
            isinstance(argument, ast.Subscript)
            and isinstance(argument.value, ast.Name)
            and isinstance(argument.slice, ast.Constant)
            and isinstance(argument.slice.value, str)
        ):
            return argument.value.id
        return None
