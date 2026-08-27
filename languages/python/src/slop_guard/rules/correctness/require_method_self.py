"""Require methods to declare the receiver the interpreter passes."""

from __future__ import annotations

import ast

from ...rule import FunctionNode, Rule


class RequireMethodSelf(Rule):
    name = "require-method-self"
    group = "correctness"
    reference = "https://docs.quantifiedcode.com/python-anti-patterns/correctness/method_has_no_argument.html"
    description = "Require a method to declare `self` or `cls`, or to be marked `@staticmethod`."

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        for statement in node.body:
            if isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self._check(statement)
        self.generic_visit(node)

    def _check(self, node: FunctionNode) -> None:
        decorators = {self.unparse(decorator).split("(")[0] for decorator in node.decorator_list}
        if "staticmethod" in decorators:
            return
        positional = [*node.args.posonlyargs, *node.args.args]
        if positional:
            expected = "cls" if "classmethod" in decorators else "self"
            if positional[0].arg != expected and node.args.vararg is None:
                self.report(
                    positional[0],
                    f"`{node.name}` receives the {'class' if expected == 'cls' else 'instance'} as "
                    f"its first argument, but calls it `{positional[0].arg}`. Name it `{expected}`, "
                    f"or mark the method `@staticmethod`.",
                )
            return
        if node.args.vararg is not None:
            return
        self.report(
            node,
            f"`{node.name}` takes no arguments, but Python passes the receiver as the first one, "
            f"so every call raises `TypeError`. Declare `self`, declare `cls` with "
            f"`@classmethod`, or mark it `@staticmethod`.",
        )
