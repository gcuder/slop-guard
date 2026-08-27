"""Coverage for the security and performance rules."""

from __future__ import annotations

import unittest

from rule_tester import RuleTestCase
from slop_guard.rules.performance import PreferSetMembership
from slop_guard.rules.security import NoExec


class TestNoExec(RuleTestCase):
    rule = NoExec
    valid = ["handlers[name]()", "run(source)"]
    invalid = ["exec(source)"]


class TestPreferSetMembership(RuleTestCase):
    rule = PreferSetMembership
    valid = ["if name in {'a', 'b'}:\n    stop()", "if name in rows:\n    stop()"]
    invalid = ["if name in ['a', 'b', 'c']:\n    stop()", "if name not in ('a', 'b'):\n    stop()"]


if __name__ == "__main__":
    unittest.main()
