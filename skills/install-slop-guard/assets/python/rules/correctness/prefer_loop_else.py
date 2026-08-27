"""Prefer a loop `else` clause over a found-flag variable."""

from __future__ import annotations

import ast

from ...rule import Rule

LoopNode = ast.For | ast.AsyncFor | ast.While


class PreferLoopElse(Rule):
    name = "prefer-loop-else"
    group = "correctness"
    reference = "https://docs.quantifiedcode.com/python-anti-patterns/correctness/not_using_else_in_a_loop.html"
    description = "Prefer a loop `else` clause to a boolean flag that records whether the loop broke."

    def visit_For(self, node: LoopNode) -> None:
        if node.orelse:
            self.generic_visit(node)
            return
        for statement in node.body:
            flag = self._flag_set_before_break(statement)
            if flag is not None:
                self.report(
                    node,
                    f"`{flag}` exists only to record that this loop broke, which is what a loop "
                    f"`else` clause already says. Drop the flag and put the not-found path in "
                    f"`else`.",
                )
                break
        self.generic_visit(node)

    visit_AsyncFor = visit_For
    visit_While = visit_For

    @staticmethod
    def _flag_set_before_break(statement: ast.stmt) -> str | None:
        if not isinstance(statement, ast.If):
            return None
        assigned: str | None = None
        breaks = False
        for child in statement.body:
            if (
                isinstance(child, ast.Assign)
                and len(child.targets) == 1
                and isinstance(child.targets[0], ast.Name)
                and isinstance(child.value, ast.Constant)
                and child.value.value is True
            ):
                assigned = child.targets[0].id
            elif isinstance(child, ast.Break):
                breaks = True
        return assigned if breaks else None
