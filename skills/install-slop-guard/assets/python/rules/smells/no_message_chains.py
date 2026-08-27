"""Reject long chains that walk through several objects."""

from __future__ import annotations

import ast
from typing import Mapping, NamedTuple

from ...rule import Rule
from ...source import SourceFile

DEFAULT_MAX_LINKS = 3


class Chain(NamedTuple):
    """How far a chain reaches, and the name it starts from."""

    links: int
    base: str


class NoMessageChains(Rule):
    name = "no-message-chains"
    group = "smells"
    reference = "https://refactoring.guru/smells/message-chains"
    description = (
        "Disallow chains of more than `max_links` attribute or call hops, 3 by default. A chain "
        "rooted at `self` counts too, because it still walks the objects after the first hop."
    )

    def __init__(self, source: SourceFile, options: Mapping[str, object] | None = None) -> None:
        super().__init__(source, options)
        self._inner: set[int] = set()

    def visit_Attribute(self, node: ast.Attribute) -> None:
        # The walk reaches the outermost attribute first, so every hop it covers is skipped later.
        if id(node) not in self._inner:
            chain = self._measure(node)
            if chain.links > self.threshold("max_links", DEFAULT_MAX_LINKS):
                self.report(
                    node,
                    f"This walks {chain.links} objects deep from `{chain.base}`, so it depends on "
                    f"how each one is built along the way, and any of them changing breaks this "
                    f"line. Ask `{chain.base}` for what you actually need.",
                )
        self.generic_visit(node)

    def _measure(self, node: ast.expr) -> Chain:
        links = 0
        current: ast.expr = node
        while True:
            if isinstance(current, ast.Attribute):
                links += 1
                self._inner.add(id(current))
                current = current.value
            elif isinstance(current, ast.Call):
                current = current.func
            elif isinstance(current, ast.Subscript):
                current = current.value
            else:
                break
        self._inner.discard(id(node))
        base = current.id if isinstance(current, ast.Name) else self.unparse(current)
        return Chain(links, base)
