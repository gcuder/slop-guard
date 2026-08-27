"""Parsed source text shared by every rule."""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from pathlib import Path

SAFETY_COMMENT = re.compile(r"#\s*SAFETY:\s*\S", re.IGNORECASE)


@dataclass(frozen=True, slots=True)
class SourceFile:
    """A single Python file, its text, and its parsed tree."""

    path: Path | None
    text: str
    tree: ast.Module

    @classmethod
    def parse(cls, text: str, path: Path | None = None) -> "SourceFile":
        tree = ast.parse(text, filename=str(path) if path is not None else "<source>")
        return cls(path=path, text=text, tree=tree)

    @property
    def lines(self) -> list[str]:
        return self.text.splitlines()

    def line(self, number: int) -> str:
        lines = self.lines
        if 1 <= number <= len(lines):
            return lines[number - 1]
        return ""

    def has_safety_comment(self, line: int) -> bool:
        """Report whether a SAFETY comment sits on this line or directly above it."""
        if SAFETY_COMMENT.search(self.line(line)):
            return True
        cursor = line - 1
        while cursor >= 1:
            stripped = self.line(cursor).strip()
            if not stripped:
                cursor -= 1
                continue
            if not stripped.startswith("#"):
                return False
            if SAFETY_COMMENT.search(stripped):
                return True
            cursor -= 1
        return False
