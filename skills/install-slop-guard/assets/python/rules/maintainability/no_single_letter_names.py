"""Reject single-letter names."""

from __future__ import annotations

import ast

from ...rule import FunctionNode, Rule

DEFAULT_ALLOWED = ("_",)


class NoSingleLetterNames(Rule):
    name = "no-single-letter-names"
    group = "maintainability"
    reference = "https://docs.quantifiedcode.com/python-anti-patterns/maintainability/using_single_letter_as_variable_name.html"
    description = (
        "Disallow single-letter names, which cannot be searched for and say nothing. The `allow` "
        "option lists exceptions."
    )

    def allowed(self) -> frozenset[str]:
        configured = self.option("allow", DEFAULT_ALLOWED)
        if isinstance(configured, (list, tuple)):
            return frozenset(str(name) for name in configured)
        return frozenset(DEFAULT_ALLOWED)

    def visit_Assign(self, node: ast.Assign) -> None:
        for target in node.targets:
            for name in [child for child in ast.walk(target) if isinstance(child, ast.Name)]:
                self._check(name, name.id, "name")
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        if isinstance(node.target, ast.Name):
            self._check(node.target, node.target.id, "name")
        self.generic_visit(node)

    def visit_FunctionDef(self, node: FunctionNode) -> None:
        self._check(node, node.name, "function")
        for parameter in self.parameters(node):
            self._check(parameter, parameter.arg, "parameter")
        self.generic_visit(node)

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self._check(node, node.name, "class")
        self.generic_visit(node)

    def visit_For(self, node: ast.For) -> None:
        for name in [child for child in ast.walk(node.target) if isinstance(child, ast.Name)]:
            self._check(name, name.id, "loop variable")
        self.generic_visit(node)

    def _check(self, node: ast.AST, name: str, kind: str) -> None:
        if len(name) == 1 and name not in self.allowed():
            self.report(
                node,
                f"The {kind} `{name}` cannot be searched for and says nothing about the value it "
                f"holds. Name it after what it means here.",
            )
