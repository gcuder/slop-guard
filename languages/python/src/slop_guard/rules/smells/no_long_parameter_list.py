"""Reject functions that take more arguments than a caller can keep straight."""

from __future__ import annotations

from ...rule import FunctionNode, Rule

DEFAULT_MAX_PARAMETERS = 4
RECEIVERS = frozenset({"self", "cls", "mcs"})


class NoLongParameterList(Rule):
    name = "no-long-parameter-list"
    group = "smells"
    reference = "https://refactoring.guru/smells/long-parameter-list"
    description = "Disallow more than `max_parameters` parameters, 4 by default, excluding `self`."

    def visit_FunctionDef(self, node: FunctionNode) -> None:
        limit = self.threshold("max_parameters", DEFAULT_MAX_PARAMETERS)
        names = [parameter.arg for parameter in self.parameters(node) if parameter.arg not in RECEIVERS]
        if len(names) > limit:
            self.report(
                node,
                f"`{node.name}` takes {len(names)} parameters, past the {limit} this project "
                f"allows. Callers have to get every position right, and the list grows with every "
                f"new case. Pass the group that travels together as one object.",
            )
        self.generic_visit(node)

    visit_AsyncFunctionDef = visit_FunctionDef
