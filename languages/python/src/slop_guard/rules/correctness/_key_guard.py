"""Shared walk for `if key not in mapping: mapping[key] = default` guards.

`prefer-defaultdict` and `prefer-setdefault` describe the same guard with different fixes, so they
share this walk and split on what the following statement does.
"""

from __future__ import annotations

import abc
import ast
from typing import NamedTuple

from ...rule import Rule


class KeyGuard(NamedTuple):
    """A `key not in mapping` guard and the value it assigns."""

    mapping: str
    key: str
    default: str


class KeyGuardRule(Rule, abc.ABC):
    """Find every missing-key guard together with the statement that follows it."""

    def visit_Module(self, node: ast.Module) -> None:
        self._scan(node.body)
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._scan(node.body)
        self.generic_visit(node)

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_For(self, node: ast.For) -> None:
        self._scan(node.body)
        self._scan(node.orelse)
        self.generic_visit(node)

    visit_AsyncFor = visit_For
    visit_While = visit_For
    visit_If = visit_For

    def visit_With(self, node: ast.With) -> None:
        self._scan(node.body)
        self.generic_visit(node)

    visit_AsyncWith = visit_With

    def _scan(self, body: list[ast.stmt]) -> None:
        for index, statement in enumerate(body):
            guard = self._guard(statement)
            if guard is None:
                continue
            following = body[index + 1] if index + 1 < len(body) else None
            self.on_guard(statement, guard, following)

    @abc.abstractmethod
    def on_guard(self, node: ast.stmt, guard: KeyGuard, following: ast.stmt | None) -> None:
        """Handle one guard. Subclasses decide which fix to recommend."""

    def _guard(self, statement: ast.stmt) -> KeyGuard | None:
        if not isinstance(statement, ast.If) or statement.orelse or len(statement.body) != 1:
            return None
        test = statement.test
        if not isinstance(test, ast.Compare) or len(test.ops) != 1:
            return None
        if not isinstance(test.ops[0], ast.NotIn) or not isinstance(test.comparators[0], ast.Name):
            return None
        mapping = test.comparators[0].id
        key = self.unparse(test.left)
        assignment = statement.body[0]
        if not isinstance(assignment, ast.Assign) or len(assignment.targets) != 1:
            return None
        if not self.is_key_of(assignment.targets[0], mapping, key):
            return None
        return KeyGuard(mapping, key, self.unparse(assignment.value))

    def is_key_of(self, node: ast.expr, mapping: str, key: str) -> bool:
        return (
            isinstance(node, ast.Subscript)
            and isinstance(node.value, ast.Name)
            and node.value.id == mapping
            and self.unparse(node.slice) == key
        )
