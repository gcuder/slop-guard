"""Reject flows that widen a known value and later cast it back."""

from __future__ import annotations

import ast

from ...rule import FunctionNode, Rule


class NoWidenThenCast(Rule):
    name = "no-widen-then-cast"
    group = "evidence"
    description = (
        "Disallow assigning a known value to `Any` or `object` and casting it back afterwards."
    )

    def visit_Module(self, node: ast.Module) -> None:
        self._check_scope(node.body)
        self.generic_visit(node)

    def visit_FunctionDef(self, node: FunctionNode) -> None:
        self._check_scope(node.body)
        self.generic_visit(node)

    visit_AsyncFunctionDef = visit_FunctionDef

    def _check_scope(self, body: list[ast.stmt]) -> None:
        widened: dict[str, ast.AST] = {}
        for statement in body:
            self._collect_widened(statement, widened)
            self._report_casts(statement, widened)

    def _collect_widened(self, statement: ast.stmt, widened: dict[str, ast.AST]) -> None:
        if isinstance(statement, ast.AnnAssign) and isinstance(statement.target, ast.Name):
            annotation = statement.annotation
            if (self.is_any(annotation) or self.is_object(annotation)) and statement.value is not None:
                widened[statement.target.id] = statement
            return
        if isinstance(statement, ast.Assign):
            for target in statement.targets:
                if isinstance(target, ast.Name) and self._is_widening_cast(statement.value):
                    widened[target.id] = statement

    def _is_widening_cast(self, value: ast.expr) -> bool:
        if not self.is_cast_call(value) or not value.args:
            return False
        target = value.args[0]
        return self.is_any(target) or self.is_object(target)

    def _report_casts(self, statement: ast.stmt, widened: dict[str, ast.AST]) -> None:
        for node in ast.walk(statement):
            if not self.is_cast_call(node) or len(node.args) < 2:
                continue
            source = node.args[1]
            if isinstance(source, ast.Name) and source.id in widened:
                self.report(
                    node,
                    f"`{source.id}` was widened earlier in this scope and is cast back here, so "
                    f"the round trip discards the type the value already had. Keep the original "
                    f"type instead.",
                )
