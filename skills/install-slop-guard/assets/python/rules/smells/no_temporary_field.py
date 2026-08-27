"""Reject attributes that only exist for part of an object's life."""

from __future__ import annotations

import ast

from ...rule import Rule


class NoTemporaryField(Rule):
    name = "no-temporary-field"
    group = "smells"
    reference = "https://refactoring.guru/smells/temporary-field"
    description = "Disallow `self` attributes first assigned outside `__init__`."

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        declared = {
            target.id
            for statement in node.body
            if isinstance(statement, ast.AnnAssign) and isinstance(statement.target, ast.Name)
            for target in [statement.target]
        }
        for statement in node.body:
            if isinstance(statement, ast.Assign):
                declared.update(
                    target.id for target in statement.targets if isinstance(target, ast.Name)
                )
        initialised: set[str] = set()
        for statement in node.body:
            if isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef)) and statement.name == "__init__":
                initialised = self._assigned(statement)
        for statement in node.body:
            if not isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if statement.name == "__init__":
                continue
            for attribute in sorted(self._assigned(statement) - initialised - declared):
                self.report(
                    statement,
                    f"`self.{attribute}` is created in `{statement.name}` rather than in "
                    f"`__init__`, so between construction and that call the attribute does not "
                    f"exist and every reader has to work out when it does. Set it in `__init__`, "
                    f"or pass it between the methods that use it.",
                )
        self.generic_visit(node)

    @staticmethod
    def _assigned(node: ast.AST) -> set[str]:
        return {
            child.attr
            for child in ast.walk(node)
            if isinstance(child, ast.Attribute)
            and isinstance(child.ctx, ast.Store)
            and isinstance(child.value, ast.Name)
            and child.value.id == "self"
        }
