"""Reject type information encoded in a name."""

from __future__ import annotations

import ast
import re

from ...rule import FunctionNode, Rule

TYPE_WORDS = ("int", "str", "float", "bool", "list", "dict", "set", "tuple", "num", "string", "arr")
PATTERN = re.compile(rf"(^|_)({'|'.join(TYPE_WORDS)})($|_)")


class NoTypeInName(Rule):
    name = "no-type-in-name"
    group = "readability"
    reference = "https://docs.quantifiedcode.com/python-anti-patterns/readability/putting_type_information_in_a_variable_name.html"
    description = "Disallow names such as `count_int` that state a type the value may not have."

    def visit_Assign(self, node: ast.Assign) -> None:
        for target in node.targets:
            for name in [child for child in ast.walk(target) if isinstance(child, ast.Name)]:
                self._check(name, name.id)
        self.generic_visit(node)

    def visit_FunctionDef(self, node: FunctionNode) -> None:
        for parameter in self.parameters(node):
            self._check(parameter, parameter.arg)
        self.generic_visit(node)

    visit_AsyncFunctionDef = visit_FunctionDef

    def _check(self, node: ast.AST, name: str) -> None:
        lowered = name.lower()
        if lowered in TYPE_WORDS:
            return
        match = PATTERN.search(lowered)
        if match is not None:
            word = match.group(2)
            self.report(
                node,
                f"`{name}` states that the value is a {word}, which the name cannot enforce and an "
                f"annotation can. Name it after what it means, and put the type in an annotation.",
            )
