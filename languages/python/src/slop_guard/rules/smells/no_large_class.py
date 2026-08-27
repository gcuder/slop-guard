"""Reject classes that carry more than one job's worth of members."""

from __future__ import annotations

import ast

from ...rule import Rule

DEFAULT_MAX_METHODS = 10
DEFAULT_MAX_ATTRIBUTES = 10


class NoLargeClass(Rule):
    name = "no-large-class"
    group = "smells"
    reference = "https://refactoring.guru/smells/large-class"
    description = (
        "Disallow classes with more than `max_methods` methods or `max_attributes` attributes, "
        "10 of each by default."
    )

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        method_limit = self.threshold("max_methods", DEFAULT_MAX_METHODS)
        attribute_limit = self.threshold("max_attributes", DEFAULT_MAX_ATTRIBUTES)
        methods = [
            statement
            for statement in node.body
            if isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]
        attributes = self._attributes(node)
        if len(methods) > method_limit:
            self.report(
                node,
                f"`{node.name}` declares {len(methods)} methods, past the {method_limit} this "
                f"project allows. A class this wide has more than one reason to change; split the "
                f"group of methods that share data into their own class.",
            )
        elif len(attributes) > attribute_limit:
            self.report(
                node,
                f"`{node.name}` holds {len(attributes)} attributes, past the {attribute_limit} "
                f"this project allows. Group the ones that change together into a smaller type.",
            )
        self.generic_visit(node)

    @staticmethod
    def _attributes(node: ast.ClassDef) -> set[str]:
        found: set[str] = set()
        for statement in node.body:
            if isinstance(statement, ast.AnnAssign) and isinstance(statement.target, ast.Name):
                found.add(statement.target.id)
            elif isinstance(statement, ast.Assign):
                found.update(
                    target.id for target in statement.targets if isinstance(target, ast.Name)
                )
        for child in ast.walk(node):
            if (
                isinstance(child, ast.Attribute)
                and isinstance(child.ctx, ast.Store)
                and isinstance(child.value, ast.Name)
                and child.value.id == "self"
            ):
                found.add(child.attr)
        return found
