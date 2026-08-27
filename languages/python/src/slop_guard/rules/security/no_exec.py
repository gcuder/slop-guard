"""Reject `exec`."""

from __future__ import annotations

import ast

from ...rule import Rule


class NoExec(Rule):
    name = "no-exec"
    group = "security"
    reference = "https://docs.quantifiedcode.com/python-anti-patterns/security/use_of_exec.html"
    description = "Disallow `exec`, which runs text as code and hides what the program does."

    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Name) and node.func.id == "exec":
            self.report(
                node,
                "`exec` runs whatever the string happens to contain, so the program's behaviour "
                "is decided at runtime and anything that reaches this string can execute code. "
                "Call the function you mean, or look it up in an explicit table.",
            )
        self.generic_visit(node)
