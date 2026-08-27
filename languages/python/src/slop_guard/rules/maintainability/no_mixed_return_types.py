"""Reject functions that return a value on one path and `None` on another."""

from __future__ import annotations

import ast

from ...rule import FunctionNode, Rule


class NoMixedReturnTypes(Rule):
    name = "no-mixed-return-types"
    group = "maintainability"
    reference = "https://docs.quantifiedcode.com/python-anti-patterns/maintainability/returning_more_than_one_variable_type_from_function_call.html"
    description = (
        "Disallow returning a value on one path and `None` on another; raise instead of handing "
        "back a placeholder."
    )

    def visit_FunctionDef(self, node: FunctionNode) -> None:
        if self._annotation_admits_none(node.returns):
            self.generic_visit(node)
            return
        returns = [
            statement
            for statement in ast.walk(node)
            if isinstance(statement, ast.Return) and self._belongs_to(node, statement)
        ]
        empty = [statement for statement in returns if self._is_none(statement)]
        valued = [statement for statement in returns if not self._is_none(statement)]
        if empty and valued:
            self.report(
                empty[0],
                f"`{node.name}` returns a value on one path and `None` on another, so every "
                f"caller has to test what came back before using it. Raise an exception on the "
                f"failing path, and keep one return type.",
            )
        self.generic_visit(node)

    visit_AsyncFunctionDef = visit_FunctionDef

    @staticmethod
    def _annotation_admits_none(annotation: ast.expr | None) -> bool:
        """A return type that already names `None` tells the caller what to expect."""
        if annotation is None:
            return False
        for node in ast.walk(annotation):
            if isinstance(node, ast.Constant) and node.value is None:
                return True
            if isinstance(node, ast.Name) and node.id in {"None", "Optional"}:
                return True
            if isinstance(node, ast.Attribute) and node.attr == "Optional":
                return True
        return False

    @staticmethod
    def _is_none(statement: ast.Return) -> bool:
        value = statement.value
        return value is None or (isinstance(value, ast.Constant) and value.value is None)

    @staticmethod
    def _belongs_to(owner: FunctionNode, statement: ast.Return) -> bool:
        """Ignore returns that belong to a function nested inside this one."""
        for node in ast.walk(owner):
            if node is owner or not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
                continue
            if any(child is statement for child in ast.walk(node)):
                return False
        return True
