"""Rules for code that costs more than it needs to: the book's performance chapter."""

from __future__ import annotations

from ...rule import Rule
from .prefer_set_membership import PreferSetMembership

RULES: tuple[type[Rule], ...] = (PreferSetMembership,)
