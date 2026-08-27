"""Reject dictionary contracts whose values carry no type evidence."""

from __future__ import annotations

import ast

from ...rule import MAPPING_PATHS, FunctionNode, Rule

BARE_CONTAINERS = frozenset({"dict", "Dict"})


class NoUnsafeDictionaryType(Rule):
    name = "no-unsafe-dictionary-type"
    group = "evidence"
    description = (
        "Disallow mapping types whose value is `Any`, `object`, or an unparameterised container."
    )

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        self._check_annotation(node.annotation)
        self.generic_visit(node)

    def visit_FunctionDef(self, node: FunctionNode) -> None:
        for parameter in self.parameters(node):
            self._check_annotation(parameter.annotation)
        self._check_annotation(node.returns)
        self.generic_visit(node)

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_TypeAlias(self, node: ast.TypeAlias) -> None:
        self._check_annotation(node.value)
        self.generic_visit(node)

    def _check_annotation(self, annotation: ast.expr | None) -> None:
        if annotation is None:
            return
        for node in ast.walk(annotation):
            if isinstance(node, ast.Subscript) and self._is_unsafe_mapping(node):
                self._report(node)
            elif isinstance(node, ast.Name) and node.id in BARE_CONTAINERS and self._is_bare(node, annotation):
                self._report(node)

    @staticmethod
    def _is_bare(node: ast.Name, annotation: ast.expr) -> bool:
        subscripted = {
            child.value
            for child in ast.walk(annotation)
            if isinstance(child, ast.Subscript)
        }
        return node not in subscripted

    def _is_unsafe_mapping(self, node: ast.Subscript) -> bool:
        if not self.imports.matches(node.value, *MAPPING_PATHS):
            return False
        value_type = self._value_type(node)
        return value_type is not None and self._is_unsafe(value_type)

    @staticmethod
    def _value_type(node: ast.Subscript) -> ast.expr | None:
        slice_node = node.slice
        if isinstance(slice_node, ast.Tuple) and len(slice_node.elts) >= 2:
            return slice_node.elts[1]
        return None

    def _is_unsafe(self, node: ast.expr) -> bool:
        if self.is_any(node):
            return True
        return isinstance(node, ast.Name) and node.id in {"object", "dict", "list", "Dict", "List"}

    def _report(self, node: ast.expr) -> None:
        self.report(
            node,
            f"`{self.unparse(node)}` describes a bag of unchecked values. Declare a dataclass, a "
            f"`TypedDict`, or a mapping to a named value type.",
        )
