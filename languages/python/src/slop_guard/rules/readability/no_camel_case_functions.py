"""Reject camelCase function and method names."""

from __future__ import annotations

import re

from ...rule import FunctionNode, Rule

CAMEL_CASE = re.compile(r"^[a-z]+([A-Z][a-z0-9]*)+$")


class NoCamelCaseFunctions(Rule):
    name = "no-camel-case-functions"
    group = "readability"
    reference = "https://docs.quantifiedcode.com/python-anti-patterns/readability/using_camelcase_in_function_names.html"
    description = "Disallow camelCase function names; PEP 8 names functions with lowercase words."

    def visit_FunctionDef(self, node: FunctionNode) -> None:
        if CAMEL_CASE.match(node.name):
            self.report(
                node,
                f"`{node.name}` is camelCase, which reads as a different language from the rest "
                f"of the file. PEP 8 names functions `{self._snake(node.name)}`.",
            )
        self.generic_visit(node)

    visit_AsyncFunctionDef = visit_FunctionDef

    @staticmethod
    def _snake(name: str) -> str:
        return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()
