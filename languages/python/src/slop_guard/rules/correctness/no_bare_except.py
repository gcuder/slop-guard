"""Reject `except` clauses that name no exception type."""

from __future__ import annotations

import ast

from ...rule import Rule


class NoBareExcept(Rule):
    name = "no-bare-except"
    group = "correctness"
    reference = "https://docs.quantifiedcode.com/python-anti-patterns/correctness/no_exception_type_specified.html"
    description = "Disallow bare `except:`, which also catches `KeyboardInterrupt` and `SystemExit`."

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        if node.type is None:
            self.report(
                node,
                "A bare `except` catches `KeyboardInterrupt` and `SystemExit` along with the "
                "errors you meant, so the program stops responding to its own shutdown. Name the "
                "exceptions this block can recover from.",
            )
        self.generic_visit(node)
