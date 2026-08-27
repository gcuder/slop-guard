"""A small valid/invalid harness mirroring the Oxlint RuleTester."""

from __future__ import annotations

import unittest
from textwrap import dedent
from typing import Mapping, Sequence

from slop_guard.rule import Rule
from slop_guard.source import SourceFile


class RuleTestCase(unittest.TestCase):
    """Base class that runs one rule over accepted and rejected snippets."""

    rule: type[Rule]
    valid: Sequence[str | tuple[str, Mapping[str, object]]] = ()
    invalid: Sequence[str | tuple[str, Mapping[str, object]]] = ()

    def _run(self, entry: str | tuple[str, Mapping[str, object]]) -> list[str]:
        code, options = entry if isinstance(entry, tuple) else (entry, {})
        source = SourceFile.parse(dedent(code).strip() + "\n")
        return [finding.message for finding in self.rule(source, options).run()]

    def test_valid(self) -> None:
        for entry in self.valid:
            code = entry[0] if isinstance(entry, tuple) else entry
            with self.subTest(code=code):
                self.assertEqual(self._run(entry), [])

    def test_invalid(self) -> None:
        for entry in self.invalid:
            code = entry[0] if isinstance(entry, tuple) else entry
            with self.subTest(code=code):
                self.assertTrue(self._run(entry), "expected at least one finding")
