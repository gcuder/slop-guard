"""Reject returning a value from `__init__`."""

from __future__ import annotations

import ast

from ...rule import FunctionNode, Rule


class NoReturnValueInInit(Rule):
    name = "no-return-value-in-init"
    group = "correctness"
    reference = "https://docs.quantifiedcode.com/python-anti-patterns/correctness/explicit_return_in_init.html"
    description = "Disallow returning a value from `__init__`, which raises `TypeError`."

    def visit_FunctionDef(self, node: FunctionNode) -> None:
        if node.name == "__init__":
            for statement in ast.walk(node):
                if isinstance(statement, ast.Return) and statement.value is not None:
                    if isinstance(statement.value, ast.Constant) and statement.value.value is None:
                        continue
                    self.report(
                        statement,
                        "`__init__` returns the new instance, so returning a value here raises "
                        "`TypeError`. Assign what you computed to an attribute, or move the work "
                        "into a classmethod constructor.",
                    )
        self.generic_visit(node)

    visit_AsyncFunctionDef = visit_FunctionDef
