"""Reject nested casts that launder a value through a wider type."""

from __future__ import annotations

import ast

from ...rule import Rule


class NoChainedCasts(Rule):
    name = "no-chained-casts"
    group = "evidence"
    description = "Disallow `cast(A, cast(B, value))`; a second cast fabricates evidence."

    def visit_Call(self, node: ast.Call) -> None:
        if self.is_cast_call(node) and len(node.args) >= 2:
            inner = node.args[1]
            if self.is_cast_call(inner):
                self.report(
                    node,
                    "This cast rewrites the result of another cast, so no check stands behind the "
                    "final type. Parse the value once and keep the parsed type.",
                )
        self.generic_visit(node)
