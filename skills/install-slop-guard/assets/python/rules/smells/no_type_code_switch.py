"""Reject branching on a type code instead of dispatching on a type."""

from __future__ import annotations

import ast
from typing import Mapping, NamedTuple

from ...rule import Rule
from ...source import SourceFile

DEFAULT_MIN_BRANCHES = 3


class Chain(NamedTuple):
    """One if/elif chain: the value it tests, how many literals it tests against, and its nodes."""

    subject: str | None
    branches: int
    nodes: tuple[int, ...]


class NoTypeCodeSwitch(Rule):
    name = "no-type-code-switch"
    group = "smells"
    reference = "https://refactoring.guru/smells/switch-statements"
    description = (
        "Disallow an if/elif chain or `match` with `min_branches` or more branches, 3 by default, "
        "testing one value against literals."
    )

    def __init__(self, source: SourceFile, options: Mapping[str, object] | None = None) -> None:
        super().__init__(source, options)
        self._reported: set[int] = set()

    def visit_If(self, node: ast.If) -> None:
        if id(node) not in self._reported:
            chain = self._chain(node)
            if chain.subject is not None and chain.branches >= self.threshold(
                "min_branches", DEFAULT_MIN_BRANCHES
            ):
                self._reported.update(chain.nodes)
                self.report(
                    node,
                    f"This tests `{chain.subject}` against {chain.branches} literal values, so "
                    f"every new value "
                    f"means editing this chain and every other one like it. Let the type decide: "
                    f"give each case its own class or handler and look it up.",
                )
        self.generic_visit(node)

    def visit_Match(self, node: ast.Match) -> None:
        literal_cases = sum(
            1 for case in node.cases if isinstance(case.pattern, (ast.MatchValue, ast.MatchSingleton))
        )
        if literal_cases >= self.threshold("min_branches", DEFAULT_MIN_BRANCHES):
            self.report(
                node,
                f"This matches `{self.unparse(node.subject)}` against {literal_cases} literal "
                f"values, so every new value means editing this block and every other one like it. "
                f"Give each case its own class or handler and look it up.",
            )
        self.generic_visit(node)

    def _chain(self, node: ast.If) -> Chain:
        subject: str | None = None
        branches = 0
        nodes: list[int] = []
        current: ast.If | None = node
        while current is not None:
            tested = self._tested_value(current.test)
            if tested is None:
                break
            if subject is None:
                subject = tested
            elif tested != subject:
                break
            branches += 1
            nodes.append(id(current))
            following = current.orelse
            current = following[0] if len(following) == 1 and isinstance(following[0], ast.If) else None
        return Chain(subject, branches, tuple(nodes))

    def _tested_value(self, test: ast.expr) -> str | None:
        if not isinstance(test, ast.Compare) or len(test.ops) != 1:
            return None
        if not isinstance(test.ops[0], (ast.Eq, ast.Is, ast.In)):
            return None
        comparator = test.comparators[0]
        if isinstance(test.ops[0], ast.In):
            if not isinstance(comparator, (ast.Tuple, ast.List, ast.Set)):
                return None
        elif not isinstance(comparator, ast.Constant):
            return None
        return self.unparse(test.left)
