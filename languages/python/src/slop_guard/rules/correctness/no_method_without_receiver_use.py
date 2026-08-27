"""Reject methods that never touch the receiver they declare."""

from __future__ import annotations

import ast

from ...rule import FunctionNode, Rule

EXEMPT_DECORATORS = frozenset({"staticmethod", "classmethod", "property", "abstractmethod"})


class NoMethodWithoutReceiverUse(Rule):
    name = "no-method-without-receiver-use"
    group = "correctness"
    reference = "https://docs.quantifiedcode.com/python-anti-patterns/correctness/method_could_be_a_function.html"
    description = "Disallow methods that never read `self` or `cls`; mark them `@staticmethod`."

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        for statement in node.body:
            if isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self._check(statement)
        self.generic_visit(node)

    def _check(self, node: FunctionNode) -> None:
        decorators = {self.unparse(decorator).split("(")[0].split(".")[-1] for decorator in node.decorator_list}
        if decorators & EXEMPT_DECORATORS:
            return
        positional = [*node.args.posonlyargs, *node.args.args]
        if not positional or positional[0].arg not in {"self", "cls"}:
            return
        receiver = positional[0].arg
        if node.name.startswith("__") and node.name.endswith("__"):
            return
        if self._is_stub(node):
            return
        used = any(
            isinstance(child, ast.Name) and child.id == receiver
            for child in ast.walk(node)
        )
        if not used:
            self.report(
                node,
                f"`{node.name}` never reads `{receiver}`, so it is a function wearing a method's "
                f"signature. Mark it `@staticmethod`, or move it out of the class.",
            )

    @staticmethod
    def _is_stub(node: FunctionNode) -> bool:
        body = [
            statement
            for statement in node.body
            if not (
                isinstance(statement, ast.Expr)
                and isinstance(statement.value, ast.Constant)
                and isinstance(statement.value.value, str)
            )
        ]
        if len(body) != 1:
            return False
        only = body[0]
        if isinstance(only, ast.Pass):
            return True
        if isinstance(only, ast.Raise):
            return True
        return (
            isinstance(only, ast.Expr)
            and isinstance(only.value, ast.Constant)
            and only.value.value is Ellipsis
        )
