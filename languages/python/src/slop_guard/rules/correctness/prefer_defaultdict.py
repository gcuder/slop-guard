"""Prefer `defaultdict` over guarding every key before updating it in place."""

from __future__ import annotations

import ast

from ._key_guard import KeyGuard, KeyGuardRule

BOOK = "https://docs.quantifiedcode.com/python-anti-patterns/correctness/not_using_defaultdict.html"


class PreferDefaultdict(KeyGuardRule):
    name = "prefer-defaultdict"
    group = "correctness"
    reference = BOOK
    description = (
        "Prefer `collections.defaultdict` to `if key not in mapping` before updating that key in "
        "place."
    )

    def on_guard(self, node: ast.stmt, guard: KeyGuard, following: ast.stmt | None) -> None:
        if isinstance(following, ast.AugAssign) and self.is_key_of(following.target, guard.mapping, guard.key):
            self.report(
                node,
                f"`{guard.mapping}` seeds `{guard.key}` by hand before updating it, so every new key needs this "
                f"guard. Build `{guard.mapping}` as a `defaultdict` and let the default appear on its own.",
            )
