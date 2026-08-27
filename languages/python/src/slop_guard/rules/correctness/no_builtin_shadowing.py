"""Reject rebinding the name of a builtin."""

from __future__ import annotations

import ast
import builtins

from ...rule import FunctionNode, Rule

BUILTINS = frozenset(name for name in dir(builtins) if not name.startswith("_"))
ALLOWED = frozenset({"_"})


class NoBuiltinShadowing(Rule):
    name = "no-builtin-shadowing"
    group = "correctness"
    reference = "https://docs.quantifiedcode.com/python-anti-patterns/correctness/assigning_to_builtin.html"
    description = "Disallow binding a name that shadows a builtin such as `list`, `id`, or `type`."

    def visit_Assign(self, node: ast.Assign) -> None:
        for target in node.targets:
            for name in self._names(target):
                self._check(node, name)
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        for name in self._names(node.target):
            self._check(node, name)
        self.generic_visit(node)

    def visit_FunctionDef(self, node: FunctionNode) -> None:
        self._check(node, node.name)
        for parameter in self.parameters(node):
            self._check(parameter, parameter.arg)
        self.generic_visit(node)

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self._check(node, node.name)
        self.generic_visit(node)

    def visit_For(self, node: ast.For) -> None:
        for name in self._names(node.target):
            self._check(node, name)
        self.generic_visit(node)

    @staticmethod
    def _names(target: ast.expr) -> list[str]:
        return [child.id for child in ast.walk(target) if isinstance(child, ast.Name)]

    def _check(self, node: ast.AST, name: str) -> None:
        if name in BUILTINS and name not in ALLOWED:
            self.report(
                node,
                f"`{name}` is a builtin, and binding it here hides the original for the rest of "
                f"this scope. Pick a name that says what the value is.",
            )
