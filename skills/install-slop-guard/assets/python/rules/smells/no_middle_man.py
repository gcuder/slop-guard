"""Reject classes that only pass calls along."""

from __future__ import annotations

import ast

from ...rule import FunctionNode, Rule

DEFAULT_MIN_METHODS = 2


class NoMiddleMan(Rule):
    name = "no-middle-man"
    group = "smells"
    reference = "https://refactoring.guru/smells/middle-man"
    description = (
        "Disallow a class whose methods all forward to one of its own fields; `min_methods` sets "
        "how many it takes, 2 by default."
    )

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        methods = [
            statement
            for statement in node.body
            if isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef))
            and statement.name != "__init__"
            and not (statement.name.startswith("__") and statement.name.endswith("__"))
        ]
        minimum = self.threshold("min_methods", DEFAULT_MIN_METHODS)
        delegates = [method for method in methods if self._delegate_target(method) is not None]
        if len(methods) >= minimum and len(delegates) == len(methods):
            target = self._delegate_target(delegates[0])
            self.report(
                node,
                f"Every method on `{node.name}` forwards to `self.{target}`, so the class adds a "
                f"hop and nothing else. Let callers talk to `{target}` directly, and keep this "
                f"class only if it is about to grow behaviour of its own.",
            )
        self.generic_visit(node)

    @staticmethod
    def _delegate_target(method: FunctionNode) -> str | None:
        body = [
            statement
            for statement in method.body
            if not (
                isinstance(statement, ast.Expr)
                and isinstance(statement.value, ast.Constant)
                and isinstance(statement.value.value, str)
            )
        ]
        if len(body) != 1:
            return None
        only = body[0]
        call = only.value if isinstance(only, (ast.Return, ast.Expr)) else None
        if not isinstance(call, ast.Call) or not isinstance(call.func, ast.Attribute):
            return None
        owner = call.func.value
        if (
            isinstance(owner, ast.Attribute)
            and isinstance(owner.value, ast.Name)
            and owner.value.id == "self"
        ):
            return owner.attr
        return None
