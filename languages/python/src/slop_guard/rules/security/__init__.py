"""Rules for code that hands control to data: the book's security chapter."""

from __future__ import annotations

from ...rule import Rule
from .no_exec import NoExec

RULES: tuple[type[Rule], ...] = (NoExec,)
