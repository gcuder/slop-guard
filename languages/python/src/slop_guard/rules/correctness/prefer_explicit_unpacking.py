"""Prefer unpacking a sequence over reading consecutive indices."""

from __future__ import annotations

import ast
from typing import NamedTuple

from ...rule import Rule


class IndexedAssignment(NamedTuple):
    """One `name = sequence[index]` statement."""

    statement: ast.stmt
    sequence: str
    index: int

MINIMUM_RUN = 2


class PreferExplicitUnpacking(Rule):
    name = "prefer-explicit-unpacking"
    group = "correctness"
    reference = "https://docs.quantifiedcode.com/python-anti-patterns/correctness/not_using_explicit_unpacking.html"
    description = "Prefer `first, second = values` to a run of index-by-index assignments."

    def visit_Module(self, node: ast.Module) -> None:
        self._check_body(node.body)
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._check_body(node.body)
        self.generic_visit(node)

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_For(self, node: ast.For) -> None:
        self._check_body(node.body)
        self.generic_visit(node)

    def visit_If(self, node: ast.If) -> None:
        self._check_body(node.body)
        self._check_body(node.orelse)
        self.generic_visit(node)

    def _check_body(self, body: list[ast.stmt]) -> None:
        run: list[IndexedAssignment] = []
        for statement in [*body, None]:
            entry = self._indexed_assignment(statement) if statement is not None else None
            if entry is not None and (
                not run or (entry.sequence == run[-1].sequence and entry.index == run[-1].index + 1)
            ):
                run.append(entry)
                continue
            if len(run) >= MINIMUM_RUN:
                sequence = run[0].sequence
                self.report(
                    run[0].statement,
                    f"These {len(run)} statements read `{sequence}` one index at a time. Unpack it "
                    f"in a single assignment so the expected length is stated once.",
                )
            run = [entry] if entry is not None else []

    @staticmethod
    def _indexed_assignment(statement: ast.stmt) -> IndexedAssignment | None:
        if not isinstance(statement, ast.Assign) or len(statement.targets) != 1:
            return None
        if not isinstance(statement.targets[0], ast.Name):
            return None
        value = statement.value
        if not isinstance(value, ast.Subscript) or not isinstance(value.value, ast.Name):
            return None
        index = value.slice
        if not isinstance(index, ast.Constant) or not isinstance(index.value, int) or isinstance(index.value, bool):
            return None
        return IndexedAssignment(statement, value.value.id, index.value)
