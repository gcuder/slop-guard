"""Reject `super()` calls whose arguments are wrong or redundant."""

from __future__ import annotations

import ast
from typing import Mapping

from ...rule import Rule
from ...source import SourceFile


class NoBadSuperArguments(Rule):
    name = "no-bad-super-arguments"
    group = "correctness"
    reference = "https://docs.quantifiedcode.com/python-anti-patterns/correctness/bad_first_argument_given_to_super.html"
    description = (
        "Disallow `super(self, Class)` and any `super()` whose first argument is not the "
        "enclosing class."
    )

    def __init__(self, source: SourceFile, options: Mapping[str, object] | None = None) -> None:
        super().__init__(source, options)
        self._classes: list[str] = []

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self._classes.append(node.name)
        self.generic_visit(node)
        self._classes.pop()

    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Name) and node.func.id == "super" and node.args:
            first = node.args[0]
            if isinstance(first, ast.Name) and first.id in {"self", "cls"}:
                self.report(
                    node,
                    "`super()` takes the class first and the instance second, so this call raises "
                    "`TypeError`. In modern Python, write `super()` with no arguments.",
                )
            elif self._classes and isinstance(first, ast.Name) and first.id != self._classes[-1]:
                self.report(
                    node,
                    f"`super({first.id}, ...)` names a class other than the enclosing "
                    f"`{self._classes[-1]}`, so it walks the wrong part of the method resolution "
                    f"order. In modern Python, write `super()` with no arguments.",
                )
        self.generic_visit(node)
