"""Reject code left behind as a comment."""

from __future__ import annotations

import ast
import io
import re
import tokenize

from ...diagnostics import Diagnostic
from ...rule import Rule

CODE_SHAPED = re.compile(r"(=|\(|\)|:\s*$|^\s*(return|import|from|if|for|while|def|class|print)\b)")
PROSE_MARKERS = ("noqa", "type:", "pragma", "SAFETY:", "TODO", "FIXME", "NOTE")


class NoCommentedOutCode(Rule):
    name = "no-commented-out-code"
    group = "smells"
    reference = "https://refactoring.guru/smells/comments"
    description = "Disallow commented-out code; the history already keeps it."

    def run(self) -> list[Diagnostic]:
        for token in self._comments():
            text = token.string.lstrip("#").strip()
            if not text or any(marker in token.string for marker in PROSE_MARKERS):
                continue
            if not CODE_SHAPED.search(text) or not self._parses(text):
                continue
            self.diagnostics.append(
                Diagnostic(
                    rule=self.name,
                    message=(
                        "This comment is code that has been switched off, so a reader has to guess "
                        "whether it still matters. Delete it; version control already remembers it."
                    ),
                    line=token.start[0],
                    column=token.start[1] + 1,
                    path=self.source.path,
                )
            )
        return self.diagnostics

    def _comments(self) -> list[tokenize.TokenInfo]:
        try:
            tokens = tokenize.generate_tokens(io.StringIO(self.source.text).readline)
            return [token for token in tokens if token.type == tokenize.COMMENT]
        except (tokenize.TokenError, IndentationError, SyntaxError):
            return []

    @staticmethod
    def _parses(text: str) -> bool:
        try:
            parsed = ast.parse(text)
        except SyntaxError:
            return False
        if not parsed.body:
            return False
        # A bare name or string is prose as often as it is code.
        only = parsed.body[0]
        return not (
            isinstance(only, ast.Expr) and isinstance(only.value, (ast.Name, ast.Constant))
        )
