"""Coverage for the maintainability rules."""

from __future__ import annotations

import unittest

from rule_tester import RuleTestCase
from slop_guard.rules.maintainability import (
    NoComputedAttributeNames,
    NoGlobalStatement,
    NoMixedReturnTypes,
    NoSingleLetterNames,
    NoWildcardImports,
    RequireWithForOpen,
)


class TestNoWildcardImports(RuleTestCase):
    rule = NoWildcardImports
    valid = ["from app.models import User", "import app.models"]
    invalid = ["from app.models import *"]


class TestRequireWithForOpen(RuleTestCase):
    rule = RequireWithForOpen
    valid = [
        "with open('rows.csv') as handle:\n    read(handle)",
        "with open('a') as first, open('b') as second:\n    join(first, second)",
    ]
    invalid = ["handle = open('rows.csv')\nread(handle)"]


class TestNoMixedReturnTypes(RuleTestCase):
    rule = NoMixedReturnTypes
    valid = [
        "def load(key):\n    if not key:\n        raise ValueError(key)\n    return rows[key]",
        "def load(key):\n    return rows[key]",
        "def load(key):\n    if not key:\n        return\n    log(key)",
    ]
    invalid = [
        "def load(key):\n    if not key:\n        return None\n    return rows[key]",
        "def load(key):\n    if not key:\n        return\n    return rows[key]",
    ]


class TestNoGlobalStatement(RuleTestCase):
    rule = NoGlobalStatement
    valid = ["def load(cache):\n    return cache"]
    invalid = ["def load():\n    global cache\n    cache = {}"]


class TestNoSingleLetterNames(RuleTestCase):
    rule = NoSingleLetterNames
    valid = [
        "rows = []",
        "for row in rows:\n    use(row)",
        ("for i in rows:\n    use(i)", {"allow": ["i"]}),
    ]
    invalid = [
        "d = {}",
        "def f(x):\n    return x",
        "for n in rows:\n    use(n)",
    ]


class TestNoComputedAttributeNames(RuleTestCase):
    rule = NoComputedAttributeNames
    valid = [
        "setattr(owner, 'name', value)",
        "values['name'] = value",
    ]
    invalid = [
        "for key, value in payload.items():\n    setattr(self, key, value)",
        "globals()['name'] = value",
    ]


if __name__ == "__main__":
    unittest.main()
