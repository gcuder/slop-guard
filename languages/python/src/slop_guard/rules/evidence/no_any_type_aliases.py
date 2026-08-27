"""Reject aliases that merely rename `Any`."""

from __future__ import annotations

import ast

from ...rule import Rule


class NoAnyTypeAliases(Rule):
    name = "no-any-type-aliases"
    group = "evidence"
    description = "Disallow type aliases whose definition is `Any`; a new name adds no evidence."

    def visit_Assign(self, node: ast.Assign) -> None:
        if self.is_any(node.value):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    self._report(node.value, target.id)
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        is_alias = self.imports.matches(node.annotation, "typing.TypeAlias", "typing_extensions.TypeAlias")
        if is_alias and self.is_any(node.value) and isinstance(node.target, ast.Name):
            self._report(node.value, node.target.id)
        self.generic_visit(node)

    def visit_TypeAlias(self, node: ast.TypeAlias) -> None:
        if self.is_any(node.value) and isinstance(node.name, ast.Name):
            self._report(node.value, node.name.id)
        self.generic_visit(node)

    def _report(self, node: ast.expr, name: str) -> None:
        self.report(
            node,
            f"`{name}` is an alias for `Any`, which hides the absence of a contract. Define the "
            f"real structure, or parse the value where it enters the program.",
        )
