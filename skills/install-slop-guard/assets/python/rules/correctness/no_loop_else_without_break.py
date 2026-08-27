"""Reject a loop `else` clause that always runs."""

from __future__ import annotations

import ast

from ...rule import Rule

LoopNode = ast.For | ast.AsyncFor | ast.While


class NoLoopElseWithoutBreak(Rule):
    name = "no-loop-else-without-break"
    group = "correctness"
    reference = "https://docs.quantifiedcode.com/python-anti-patterns/correctness/else_clause_on_loop_without_a_break_statement.html"
    description = "Disallow `else` on a loop whose body contains no `break`."

    def visit_For(self, node: LoopNode) -> None:
        if node.orelse and not self._has_break(node):
            self.report(
                node.orelse[0],
                "This loop has no `break`, so its `else` clause runs every time and reads as a "
                "fallback that never fires. Add the `break` the `else` is waiting for, or move "
                "the block after the loop.",
            )
        self.generic_visit(node)

    visit_AsyncFor = visit_For
    visit_While = visit_For

    @staticmethod
    def _has_break(loop: LoopNode) -> bool:
        """Look for a `break` bound to this loop, not to a nested loop or function."""
        pending: list[ast.AST] = list(loop.body)
        while pending:
            node = pending.pop()
            if isinstance(node, ast.Break):
                return True
            if isinstance(
                node,
                (ast.For, ast.AsyncFor, ast.While, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef),
            ):
                continue
            pending.extend(ast.iter_child_nodes(node))
        return False
