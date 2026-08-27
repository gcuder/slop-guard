"""Reject function contracts that hand `Any` back to callers."""

from __future__ import annotations

import ast

from ...rule import FunctionNode, Rule


class NoAnyReturns(Rule):
    name = "no-any-returns"
    group = "evidence"
    description = "Disallow return annotations that contain `Any`; name what the function produces."

    def visit_FunctionDef(self, node: FunctionNode) -> None:
        self._check(node.returns, node.name)
        self.generic_visit(node)

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        # Callable[..., Any] contracts declared as attributes or aliases.
        annotation = node.annotation
        if self.imports.matches(annotation, "typing.Callable", "collections.abc.Callable"):
            found = self._callable_return(annotation)
            if found is not None:
                self._report(found, self.unparse(node.target))
        self.generic_visit(node)

    def _callable_return(self, annotation: ast.expr) -> ast.expr | None:
        if not isinstance(annotation, ast.Subscript):
            return None
        slice_node = annotation.slice
        if not isinstance(slice_node, ast.Tuple) or not slice_node.elts:
            return None
        return self.contains_any(slice_node.elts[-1])

    def _check(self, returns: ast.expr | None, name: str) -> None:
        found = self.contains_any(returns)
        if found is not None:
            self._report(found, name)

    def _report(self, node: ast.expr, name: str) -> None:
        self.report(
            node,
            f"`{name}` returns `Any`, so every caller inherits unchecked data. Return a named "
            f"type, a dataclass, or a parsed model instead.",
        )
