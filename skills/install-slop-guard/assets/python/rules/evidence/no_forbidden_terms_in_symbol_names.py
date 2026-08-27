"""Reject placeholder vocabulary in declared symbol names."""

from __future__ import annotations

import ast

from ...rule import FunctionNode, Rule

DEFAULT_TERMS = ("shape",)


class NoForbiddenTermsInSymbolNames(Rule):
    name = "no-forbidden-terms-in-symbol-names"
    group = "evidence"
    description = (
        "Disallow placeholder words such as `shape` in declared symbol names; the `terms` "
        "option sets the list."
    )

    def terms(self) -> tuple[str, ...]:
        configured = self.option("terms", DEFAULT_TERMS)
        if isinstance(configured, (list, tuple)):
            return tuple(str(term).lower() for term in configured)
        return DEFAULT_TERMS

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self._check(node, node.name, "class")
        self.generic_visit(node)

    def visit_FunctionDef(self, node: FunctionNode) -> None:
        self._check(node, node.name, "function")
        for parameter in self.parameters(node):
            self._check(parameter, parameter.arg, "parameter")
        self.generic_visit(node)

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_Assign(self, node: ast.Assign) -> None:
        for target in node.targets:
            if isinstance(target, ast.Name):
                self._check(target, target.id, "name")
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        if isinstance(node.target, ast.Name):
            self._check(node.target, node.target.id, "name")
        self.generic_visit(node)

    def _check(self, node: ast.AST, name: str, kind: str) -> None:
        words = {word for word in self._words(name) if word}
        for term in self.terms():
            if term in words:
                self.report(
                    node,
                    f"The {kind} name `{name}` uses the placeholder word `{term}`, which describes "
                    f"no domain concept. Name what the value means to the program.",
                )
                return

    @staticmethod
    def _words(name: str) -> list[str]:
        collected: list[str] = []
        current = ""
        for character in name:
            if character == "_":
                collected.append(current.lower())
                current = ""
            elif character.isupper() and current:
                collected.append(current.lower())
                current = character
            else:
                current += character
        collected.append(current.lower())
        return collected
