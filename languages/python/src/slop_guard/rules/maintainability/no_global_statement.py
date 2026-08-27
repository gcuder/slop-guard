"""Reject the `global` statement."""

from __future__ import annotations

import ast

from ...rule import Rule


class NoGlobalStatement(Rule):
    name = "no-global-statement"
    group = "maintainability"
    reference = "https://docs.quantifiedcode.com/python-anti-patterns/maintainability/using_the_global_statement.html"
    description = "Disallow `global`; pass state in and return it instead of rebinding a module name."

    def visit_Global(self, node: ast.Global) -> None:
        names = ", ".join(f"`{name}`" for name in node.names)
        self.report(
            node,
            f"`global` lets this function rebind {names} for the whole module, so a reader cannot "
            f"tell what changed it. Take the value as an argument and return the new one.",
        )
        self.generic_visit(node)
