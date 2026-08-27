"""Reject runs of same-typed primitive parameters that a domain type should carry."""

from __future__ import annotations

import ast

from ...rule import FunctionNode, Rule

PRIMITIVES = frozenset({"str", "int", "float", "bool", "bytes"})
DEFAULT_MAX_SAME_TYPE = 2
RECEIVERS = frozenset({"self", "cls", "mcs"})


class NoPrimitiveObsession(Rule):
    name = "no-primitive-obsession"
    group = "smells"
    reference = "https://refactoring.guru/smells/primitive-obsession"
    description = (
        "Disallow more than `max_same_type` parameters of the same primitive type, 2 by default; "
        "give the domain concept a type."
    )

    def visit_FunctionDef(self, node: FunctionNode) -> None:
        limit = self.threshold("max_same_type", DEFAULT_MAX_SAME_TYPE)
        counts: dict[str, list[str]] = {}
        for parameter in self.parameters(node):
            if parameter.arg in RECEIVERS:
                continue
            annotation = parameter.annotation
            if isinstance(annotation, ast.Name) and annotation.id in PRIMITIVES:
                counts.setdefault(annotation.id, []).append(parameter.arg)
        for primitive, names in counts.items():
            if len(names) > limit:
                listed = ", ".join(f"`{name}`" for name in names)
                self.report(
                    node,
                    f"`{node.name}` takes {len(names)} `{primitive}` parameters ({listed}), so "
                    f"any two of them can be swapped at a call site and nothing complains. Give the "
                    f"values a type of their own.",
                )
        self.generic_visit(node)

    visit_AsyncFunctionDef = visit_FunctionDef
