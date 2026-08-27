"""Prefer a named type to a long anonymous tuple return."""

from __future__ import annotations

import ast

from ...rule import FunctionNode, Rule

MINIMUM_ELEMENTS = 3


class PreferNamedTuple(Rule):
    name = "prefer-named-tuple"
    group = "readability"
    reference = "https://docs.quantifiedcode.com/python-anti-patterns/readability/not_using_named_tuples_when_returning_more_than_one_value.html"
    description = (
        "Prefer a `NamedTuple` or dataclass to returning three or more values in a bare tuple."
    )

    def visit_FunctionDef(self, node: FunctionNode) -> None:
        for statement in node.body:
            for child in ast.walk(statement):
                if isinstance(child, ast.Return) and isinstance(child.value, ast.Tuple):
                    if len(child.value.elts) >= MINIMUM_ELEMENTS:
                        self.report(
                            child,
                            f"`{node.name}` returns {len(child.value.elts)} values in a bare tuple, "
                            f"so every caller reads them by position and a reordering breaks them "
                            f"silently. Return a `NamedTuple` or a dataclass.",
                        )
                        break
        self.generic_visit(node)

    visit_AsyncFunctionDef = visit_FunctionDef
