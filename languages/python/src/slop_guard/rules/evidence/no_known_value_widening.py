"""Reject annotations that throw away what the assigned value already proves."""

from __future__ import annotations

import ast

from ...rule import MAPPING_PATHS, Rule


class NoKnownValueWidening(Rule):
    name = "no-known-value-widening"
    group = "evidence"
    description = (
        "Disallow annotations that widen a known literal to `Any`, `object`, or an open mapping."
    )

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        if node.value is not None:
            self._check(node.annotation, node.value, self.unparse(node.target))
        self.generic_visit(node)

    def _check(self, annotation: ast.expr, value: ast.expr, target: str) -> None:
        if self.is_any(annotation) or self.is_object(annotation):
            self.report(
                annotation,
                f"`{target}` is annotated `{self.unparse(annotation)}` even though its value has a "
                f"type. Drop the annotation and keep inference, or name the real type.",
            )
            return
        if self._is_literal_mapping(value) and self._is_open_mapping(annotation):
            self.report(
                annotation,
                f"`{target}` lists its keys but is annotated `{self.unparse(annotation)}`, which "
                f"discards them. Use `Final` and inference, a `TypedDict`, or a `Literal` key type.",
            )

    @staticmethod
    def _is_literal_mapping(value: ast.expr) -> bool:
        return (
            isinstance(value, ast.Dict)
            and len(value.keys) > 0
            and all(isinstance(key, ast.Constant) for key in value.keys)
        )

    def _is_open_mapping(self, annotation: ast.expr) -> bool:
        if not isinstance(annotation, ast.Subscript):
            return False
        if not self.imports.matches(annotation.value, *MAPPING_PATHS):
            return False
        slice_node = annotation.slice
        if not isinstance(slice_node, ast.Tuple) or len(slice_node.elts) < 2:
            return False
        key = slice_node.elts[0]
        return isinstance(key, ast.Name) and key.id in {"str", "int", "bytes"}
