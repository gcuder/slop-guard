"""Reject the same group of parameters travelling between functions."""

from __future__ import annotations

import ast

from ...rule import FunctionNode, Rule

DEFAULT_MIN_GROUP = 3
RECEIVERS = frozenset({"self", "cls", "mcs"})


class NoDataClumps(Rule):
    name = "no-data-clumps"
    group = "smells"
    reference = "https://refactoring.guru/smells/data-clumps"
    description = (
        "Disallow the same group of `min_group` parameter names, 3 by default, appearing in more "
        "than one function in a module."
    )

    def run(self) -> list:
        minimum = self.threshold("min_group", DEFAULT_MIN_GROUP)
        seen: dict[frozenset[str], tuple[str, ast.AST]] = {}
        for node in ast.walk(self.source.tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            names = frozenset(
                parameter.arg for parameter in self.parameters(node) if parameter.arg not in RECEIVERS
            )
            if len(names) < minimum:
                continue
            earlier = seen.get(names)
            if earlier is None:
                seen[names] = (node.name, node)
                continue
            listed = ", ".join(f"`{name}`" for name in sorted(names))
            self.report(
                node,
                f"`{node.name}` and `{earlier[0]}` both take {listed}. Values that travel "
                f"together belong to one thing; give them a type and pass that instead.",
            )
        return self.diagnostics
