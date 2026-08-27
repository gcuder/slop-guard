"""Coverage for the correctness rules."""

from __future__ import annotations

import unittest

from rule_tester import RuleTestCase
from slop_guard.rules.correctness import (
    NoBadSuperArguments,
    NoBareExcept,
    NoBuiltinShadowing,
    NoJavaStyleAccessors,
    NoLambdaAssignment,
    NoLoopElseWithoutBreak,
    NoMethodWithoutReceiverUse,
    NoMixedIndentation,
    NoMutableDefaultArgument,
    NoProtectedMemberAccess,
    NoReturnValueInInit,
    NoTabIndentation,
    NoUnreachableExceptClause,
    PreferDefaultdict,
    PreferDictGet,
    PreferExplicitUnpacking,
    PreferLoopElse,
    PreferSetdefault,
    RequireExitSignature,
    RequireMethodSelf,
)


class TestNoProtectedMemberAccess(RuleTestCase):
    rule = NoProtectedMemberAccess
    valid = [
        "value = owner.name",
        "class Store:\n    def load(self):\n        return self._rows",
        "value = owner.__class__",
    ]
    invalid = ["value = store._rows", "store._rows = []"]


class TestNoLambdaAssignment(RuleTestCase):
    rule = NoLambdaAssignment
    valid = ["def double(value):\n    return value * 2", "handlers = {'a': lambda value: value}"]
    invalid = ["double = lambda value: value * 2", "double: Callable = lambda value: value"]


class TestNoBuiltinShadowing(RuleTestCase):
    rule = NoBuiltinShadowing
    valid = ["rows = []", "def load(values):\n    return values"]
    invalid = ["list = [1]", "def load(id):\n    return id", "for type in kinds:\n    pass"]


class TestNoUnreachableExceptClause(RuleTestCase):
    rule = NoUnreachableExceptClause
    valid = [
        "try:\n    run()\nexcept KeyError:\n    pass\nexcept Exception:\n    raise",
        "try:\n    run()\nexcept KeyError:\n    pass\nexcept ValueError:\n    raise",
    ]
    invalid = [
        "try:\n    run()\nexcept Exception:\n    pass\nexcept KeyError:\n    raise",
        "try:\n    run()\nexcept LookupError:\n    pass\nexcept IndexError:\n    raise",
    ]


class TestNoBadSuperArguments(RuleTestCase):
    rule = NoBadSuperArguments
    valid = [
        "class Square(Rectangle):\n    def __init__(self):\n        super().__init__()",
        "class Square(Rectangle):\n    def __init__(self):\n        super(Square, self).__init__()",
    ]
    invalid = [
        "class Square(Rectangle):\n    def __init__(self):\n        super(self, Square).__init__()",
        "class Square(Rectangle):\n    def __init__(self):\n        super(Rectangle, self).__init__()",
    ]


class TestNoLoopElseWithoutBreak(RuleTestCase):
    rule = NoLoopElseWithoutBreak
    valid = [
        "for row in rows:\n    if row:\n        break\nelse:\n    report()",
        "for row in rows:\n    use(row)",
        "while running:\n    if done:\n        break\nelse:\n    report()",
    ]
    invalid = [
        "for row in rows:\n    use(row)\nelse:\n    report()",
        "for row in rows:\n    for cell in row:\n        break\nelse:\n    report()",
    ]


class TestRequireExitSignature(RuleTestCase):
    rule = RequireExitSignature
    valid = [
        "class Session:\n    def __exit__(self, kind, error, traceback):\n        return False",
        "class Session:\n    def __exit__(self, *details):\n        return False",
    ]
    invalid = [
        "class Session:\n    def __exit__(self):\n        return False",
        "class Session:\n    def __exit__(self, error):\n        return False",
    ]


class TestNoReturnValueInInit(RuleTestCase):
    rule = NoReturnValueInInit
    valid = [
        "class Store:\n    def __init__(self):\n        self.rows = []",
        "class Store:\n    def __init__(self):\n        if broken:\n            return\n        self.rows = []",
    ]
    invalid = ["class Store:\n    def __init__(self):\n        return self"]


class TestNoJavaStyleAccessors(RuleTestCase):
    rule = NoJavaStyleAccessors
    valid = [
        "class Store:\n    @property\n    def rows(self):\n        return self._rows",
        "class Store:\n    def get_rows(self):\n        return load(self._rows)",
    ]
    invalid = [
        "class Store:\n    def get_rows(self):\n        return self._rows",
        "class Store:\n    def set_rows(self, rows):\n        self._rows = rows",
    ]


class TestNoTabIndentation(RuleTestCase):
    rule = NoTabIndentation
    valid = ["def load():\n    return 1"]
    invalid = ["def load():\n\treturn 1"]


class TestNoMixedIndentation(RuleTestCase):
    rule = NoMixedIndentation
    valid = ["def load():\n    return 1", "def load():\n\treturn 1"]
    invalid = ["def load():\n \treturn 1"]


class TestRequireMethodSelf(RuleTestCase):
    rule = RequireMethodSelf
    valid = [
        "class Store:\n    def load(self):\n        return 1",
        "class Store:\n    @staticmethod\n    def load():\n        return 1",
        "class Store:\n    @classmethod\n    def build(cls):\n        return cls()",
    ]
    invalid = [
        "class Store:\n    def load():\n        return 1",
        "class Store:\n    @classmethod\n    def build():\n        return 1",
        "class Store:\n    def load(store):\n        return store",
    ]


class TestNoMethodWithoutReceiverUse(RuleTestCase):
    rule = NoMethodWithoutReceiverUse
    valid = [
        "class Store:\n    def load(self):\n        return self.rows",
        "class Store:\n    @staticmethod\n    def area(width, height):\n        return width * height",
        "class Store:\n    def load(self):\n        raise NotImplementedError",
    ]
    invalid = ["class Rectangle:\n    def area(self, width, height):\n        return width * height"]


class TestNoMutableDefaultArgument(RuleTestCase):
    rule = NoMutableDefaultArgument
    valid = [
        "def load(rows=None):\n    return rows or []",
        "def load(count=0):\n    return count",
    ]
    invalid = [
        "def load(rows=[]):\n    return rows",
        "def load(index={}):\n    return index",
        "def load(seen=set()):\n    return seen",
    ]


class TestNoBareExcept(RuleTestCase):
    rule = NoBareExcept
    valid = ["try:\n    run()\nexcept OSError:\n    retry()"]
    invalid = ["try:\n    run()\nexcept:\n    retry()"]


class TestPreferDefaultdict(RuleTestCase):
    rule = PreferDefaultdict
    valid = [
        "counts = defaultdict(int)\ncounts['k'] += 1",
        "if 'k' not in counts:\n    counts['k'] = []\ncounts['k'].append(1)",
    ]
    invalid = ["if 'k' not in counts:\n    counts['k'] = 0\ncounts['k'] += 1"]


class TestPreferSetdefault(RuleTestCase):
    rule = PreferSetdefault
    valid = [
        "rows.setdefault('k', []).append(1)",
        "if 'k' not in counts:\n    counts['k'] = 0\ncounts['k'] += 1",
    ]
    invalid = ["if 'k' not in rows:\n    rows['k'] = []\nrows['k'].append(1)"]


class TestPreferDictGet(RuleTestCase):
    rule = PreferDictGet
    valid = ["timeout = options.get('timeout', 30)"]
    invalid = ["if 'timeout' in options:\n    timeout = options['timeout']\nelse:\n    timeout = 30"]


class TestPreferLoopElse(RuleTestCase):
    rule = PreferLoopElse
    valid = [
        "for row in rows:\n    if row:\n        break\nelse:\n    report()",
        "for row in rows:\n    found = True",
    ]
    invalid = ["for row in rows:\n    if row == target:\n        found = True\n        break"]


class TestPreferExplicitUnpacking(RuleTestCase):
    rule = PreferExplicitUnpacking
    valid = [
        "first, second = values",
        "first = values[0]\nlast = values[7]",
        "first = values[0]\nsecond = others[1]",
    ]
    invalid = [
        "first = values[0]\nsecond = values[1]",
        "def load():\n    a = values[0]\n    b = values[1]\n    c = values[2]\n    return a, b, c",
    ]


if __name__ == "__main__":
    unittest.main()
