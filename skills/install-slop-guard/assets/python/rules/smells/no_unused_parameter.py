"""Reject parameters that the function never reads."""

from __future__ import annotations

import ast

from ...rule import FunctionNode, Rule

RECEIVERS = frozenset({"self", "cls", "mcs"})
DYNAMIC_LOOKUPS = frozenset({"locals", "vars", "eval", "exec"})


class NoUnusedParameter(Rule):
    name = "no-unused-parameter"
    group = "smells"
    reference = "https://refactoring.guru/smells/speculative-generality"
    description = (
        "Disallow parameters the body never reads; a name prefixed with an underscore is exempt."
    )

    def visit_FunctionDef(self, node: FunctionNode) -> None:
        if self._is_stub(node) or self._is_override(node) or self._reads_scope(node):
            self.generic_visit(node)
            return
        used = {child.id for child in ast.walk(node) if isinstance(child, ast.Name)}
        for parameter in self.parameters(node):
            name = parameter.arg
            if name in RECEIVERS or name.startswith("_") or name in used:
                continue
            self.report(
                parameter,
                f"`{node.name}` takes `{name}` and never reads it, so the argument every caller "
                f"passes does nothing. Remove it, or prefix the name with an underscore when an "
                f"interface forces the signature.",
            )
        self.generic_visit(node)

    visit_AsyncFunctionDef = visit_FunctionDef

    def _is_override(self, node: FunctionNode) -> bool:
        return any(
            self.unparse(decorator).split(".")[-1] in {"override", "abstractmethod", "overload"}
            for decorator in node.decorator_list
        )

    @staticmethod
    def _reads_scope(node: FunctionNode) -> bool:
        return any(
            isinstance(child, ast.Call)
            and isinstance(child.func, ast.Name)
            and child.func.id in DYNAMIC_LOOKUPS
            for child in ast.walk(node)
        )

    @staticmethod
    def _is_stub(node: FunctionNode) -> bool:
        body = [
            statement
            for statement in node.body
            if not (
                isinstance(statement, ast.Expr)
                and isinstance(statement.value, ast.Constant)
                and isinstance(statement.value.value, str)
            )
        ]
        if len(body) != 1:
            return False
        only = body[0]
        if isinstance(only, (ast.Pass, ast.Raise)):
            return True
        return (
            isinstance(only, ast.Expr)
            and isinstance(only.value, ast.Constant)
            and only.value.value is Ellipsis
        )
