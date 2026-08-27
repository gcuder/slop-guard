"""Reject methods more interested in another object than in their own."""

from __future__ import annotations

import ast

from ...rule import FunctionNode, Rule

DEFAULT_MIN_ACCESSES = 5
DOMINANCE = 2
RECEIVERS = frozenset({"self", "cls", "mcs"})


class NoFeatureEnvy(Rule):
    name = "no-feature-envy"
    group = "smells"
    reference = "https://refactoring.guru/smells/feature-envy"
    description = (
        "Disallow a method that reads one other object's members `min_accesses` times or more, "
        "5 by default, and at least twice as often as its own."
    )

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        for statement in node.body:
            if isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self._check(statement)
        self.generic_visit(node)

    def _check(self, node: FunctionNode) -> None:
        minimum = self.threshold("min_accesses", DEFAULT_MIN_ACCESSES)
        parameters = {parameter.arg for parameter in self.parameters(node)} - RECEIVERS
        own = 0
        foreign: dict[str, int] = {}
        for child in ast.walk(node):
            if not isinstance(child, ast.Attribute) or not isinstance(child.value, ast.Name):
                continue
            owner = child.value.id
            if owner in RECEIVERS:
                own += 1
            elif owner in parameters:
                foreign[owner] = foreign.get(owner, 0) + 1
        for owner, count in foreign.items():
            if count >= minimum and count > own * DOMINANCE:
                self.report(
                    node,
                    f"`{node.name}` reads `{owner}` {count} times and its own object {own} "
                    f"time(s), so the decision this method makes is really about `{owner}`. Move "
                    f"the method there, and call it from here.",
                )
