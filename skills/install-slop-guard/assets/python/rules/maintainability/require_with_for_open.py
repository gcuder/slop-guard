"""Require `with` when opening a file."""

from __future__ import annotations

import ast
from typing import Mapping

from ...rule import Rule
from ...source import SourceFile


class RequireWithForOpen(Rule):
    name = "require-with-for-open"
    group = "maintainability"
    reference = "https://docs.quantifiedcode.com/python-anti-patterns/maintainability/not_using_with_to_open_files.html"
    description = "Require `open()` to be used in a `with` statement so the file always closes."

    def __init__(self, source: SourceFile, options: Mapping[str, object] | None = None) -> None:
        super().__init__(source, options)
        self._managed: set[int] = set()

    def visit_With(self, node: ast.With) -> None:
        for item in node.items:
            for child in ast.walk(item.context_expr):
                self._managed.add(id(child))
        self.generic_visit(node)

    visit_AsyncWith = visit_With

    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Name) and node.func.id == "open" and id(node) not in self._managed:
            self.report(
                node,
                "This file is opened outside a `with` block, so an exception before `close()` "
                "leaks the handle. Write `with open(...) as handle:`.",
            )
        self.generic_visit(node)
