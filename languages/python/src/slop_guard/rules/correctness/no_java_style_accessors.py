"""Reject Java-style getters and setters where a property belongs."""

from __future__ import annotations

import ast

from ...rule import FunctionNode, Rule


class NoJavaStyleAccessors(Rule):
    name = "no-java-style-accessors"
    group = "correctness"
    reference = "https://docs.quantifiedcode.com/python-anti-patterns/correctness/implementing_java-style_getters_and_setters.html"
    description = "Disallow `get_x`/`set_x` methods that only move a single attribute."

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        for statement in node.body:
            if isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self._check(statement)
        self.generic_visit(node)

    def _check(self, node: FunctionNode) -> None:
        if any(self.unparse(decorator).endswith("setter") for decorator in node.decorator_list):
            return
        if self.unparse_decorators(node) & {"property", "staticmethod", "classmethod"}:
            return
        if node.name.startswith("get_") and self._is_plain_getter(node):
            self.report(node, self._message(node.name, direction="read"))
        elif node.name.startswith("set_") and self._is_plain_setter(node):
            self.report(node, self._message(node.name, direction="write"))

    def unparse_decorators(self, node: FunctionNode) -> set[str]:
        return {self.unparse(decorator) for decorator in node.decorator_list}

    @staticmethod
    def _is_plain_getter(node: FunctionNode) -> bool:
        body = [item for item in node.body if not _is_docstring(item)]
        return (
            len(body) == 1
            and isinstance(body[0], ast.Return)
            and isinstance(body[0].value, ast.Attribute)
        )

    @staticmethod
    def _is_plain_setter(node: FunctionNode) -> bool:
        body = [item for item in node.body if not _is_docstring(item)]
        return (
            len(body) == 1
            and isinstance(body[0], ast.Assign)
            and len(body[0].targets) == 1
            and isinstance(body[0].targets[0], ast.Attribute)
        )

    @staticmethod
    def _message(method: str, *, direction: str) -> str:
        attribute = method[4:]
        return (
            f"`{method}` only {direction}s one attribute, so it adds a method call without adding "
            f"a decision. Expose `{attribute}` as an attribute, and reach for `@property` when "
            f"it later needs logic."
        )


def _is_docstring(node: ast.stmt) -> bool:
    return isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str)
