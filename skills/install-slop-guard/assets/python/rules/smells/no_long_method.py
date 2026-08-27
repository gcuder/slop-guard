"""Reject methods that have grown past what one reader can hold."""

from __future__ import annotations

import ast

from ...rule import FunctionNode, Rule

DEFAULT_MAX_STATEMENTS = 20


class NoLongMethod(Rule):
    name = "no-long-method"
    group = "smells"
    reference = "https://refactoring.guru/smells/long-method"
    description = "Disallow functions longer than `max_statements` statements, 20 by default."

    def visit_FunctionDef(self, node: FunctionNode) -> None:
        limit = self.threshold("max_statements", DEFAULT_MAX_STATEMENTS)
        count = self._statements(node)
        if count > limit:
            self.report(
                node,
                f"`{node.name}` runs {count} statements, past the {limit} this project allows, so "
                f"a reader has to hold all of it at once to change any of it. Pull the middle steps "
                f"out into named functions.",
            )
        self.generic_visit(node)

    visit_AsyncFunctionDef = visit_FunctionDef

    @staticmethod
    def _statements(node: FunctionNode) -> int:
        """Count the statements this function runs, not those of functions defined inside it."""
        total = 0
        pending: list[ast.AST] = list(node.body)
        while pending:
            current = pending.pop()
            if isinstance(current, ast.stmt):
                total += 1
            if isinstance(current, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                continue
            pending.extend(ast.iter_child_nodes(current))
        return total
