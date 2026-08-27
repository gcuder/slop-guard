"""Prefer `setdefault` over guarding a key before initialising it."""

from __future__ import annotations

import ast

from ._key_guard import KeyGuard, KeyGuardRule

BOOK = (
    "https://docs.quantifiedcode.com/python-anti-patterns/correctness/"
    "not_using_setdefault_to_initialize_a_dictionary.html"
)


class PreferSetdefault(KeyGuardRule):
    name = "prefer-setdefault"
    group = "correctness"
    reference = BOOK
    description = (
        "Prefer `mapping.setdefault(key, default)` to `if key not in mapping` before assigning that "
        "key."
    )

    def on_guard(self, node: ast.stmt, guard: KeyGuard, following: ast.stmt | None) -> None:
        # An in-place update right after the guard is prefer-defaultdict's case, not this one.
        if isinstance(following, ast.AugAssign) and self.is_key_of(following.target, guard.mapping, guard.key):
            return
        self.report(
            node,
            f"This checks for `{guard.key}` and then assigns it, which `setdefault` does in one step. "
            f"Write `{guard.mapping}.setdefault({guard.key}, {guard.default})`.",
        )
