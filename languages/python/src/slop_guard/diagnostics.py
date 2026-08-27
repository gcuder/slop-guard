"""Diagnostic records produced by rules."""

from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class Diagnostic:
    """A single rule violation at a source position."""

    rule: str
    message: str
    line: int
    column: int
    path: Path | None = None

    def render(self) -> str:
        location = self.path.as_posix() if self.path is not None else "<source>"
        return f"{location}:{self.line}:{self.column}: {self.rule} {self.message}"

    def as_dict(self) -> dict[str, object]:
        return {
            "rule": self.rule,
            "message": self.message,
            "line": self.line,
            "column": self.column,
            "path": self.path.as_posix() if self.path is not None else None,
        }


LOCATED = (ast.expr, ast.stmt, ast.excepthandler, ast.arg, ast.alias, ast.pattern)


def position(node: ast.AST) -> tuple[int, int]:
    """Return the one-based line and column of a node that carries a position."""
    if isinstance(node, LOCATED):
        return node.lineno, node.col_offset + 1
    return 1, 1
