"""Reject the bare `object` type on function inputs."""

from __future__ import annotations

from ...rule import FunctionNode, Rule


class NoObjectParameters(Rule):
    name = "no-object-parameters"
    group = "evidence"
    description = "Disallow `object` function parameters; accept the type the function actually needs."

    def visit_FunctionDef(self, node: FunctionNode) -> None:
        for parameter in self.parameters(node):
            if self.is_object(parameter.annotation):
                self.report(
                    parameter.annotation or parameter,
                    f"Parameter `{parameter.arg}` accepts `object`, which admits every value and "
                    f"promises nothing. Accept the named type this function reads.",
                )
        self.generic_visit(node)

    visit_AsyncFunctionDef = visit_FunctionDef
