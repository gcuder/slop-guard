"""Resolve local names back to the modules they were imported from."""

from __future__ import annotations

import ast


class ImportIndex(ast.NodeVisitor):
    """Map local names to canonical dotted paths such as `typing.Any`."""

    def __init__(self) -> None:
        self.symbols: dict[str, str] = {}
        self.modules: dict[str, str] = {}

    @classmethod
    def build(cls, tree: ast.Module) -> "ImportIndex":
        index = cls()
        index.visit(tree)
        return index

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            self.modules[alias.asname or alias.name] = alias.name

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        module = node.module or ""
        for alias in node.names:
            local = alias.asname or alias.name
            self.symbols[local] = f"{module}.{alias.name}" if module else alias.name

    def resolve(self, node: ast.expr | None) -> str | None:
        """Return the canonical dotted path a type expression refers to."""
        if isinstance(node, ast.Name):
            return self.symbols.get(node.id, node.id)
        if isinstance(node, ast.Attribute):
            base = self._resolve_module(node.value)
            return f"{base}.{node.attr}" if base is not None else None
        if isinstance(node, ast.Subscript):
            return self.resolve(node.value)
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            try:
                return self.resolve(ast.parse(node.value, mode="eval").body)
            except SyntaxError:
                return None
        return None

    def _resolve_module(self, node: ast.expr) -> str | None:
        if isinstance(node, ast.Name):
            return self.modules.get(node.id, self.symbols.get(node.id, node.id))
        if isinstance(node, ast.Attribute):
            base = self._resolve_module(node.value)
            return f"{base}.{node.attr}" if base is not None else None
        return None

    def matches(self, node: ast.expr | None, *paths: str) -> bool:
        """Report whether a type expression resolves to one of the given paths."""
        resolved = self.resolve(node)
        if resolved is None:
            return False
        if resolved in paths:
            return True
        tail = resolved.rsplit(".", 1)[-1]
        return any(tail == path.rsplit(".", 1)[-1] and "." not in resolved for path in paths)
