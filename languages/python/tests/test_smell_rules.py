"""Coverage for the code smell rules."""

from __future__ import annotations

import unittest

from rule_tester import RuleTestCase
from slop_guard.rules.smells import (
    NoCommentedOutCode,
    NoDataClass,
    NoDataClumps,
    NoDuplicateCode,
    NoFeatureEnvy,
    NoLargeClass,
    NoLazyClass,
    NoLongMethod,
    NoLongParameterList,
    NoMessageChains,
    NoMiddleMan,
    NoPrimitiveObsession,
    NoRefusedBequest,
    NoTemporaryField,
    NoTypeCodeSwitch,
    NoUnreachableCode,
    NoUnusedParameter,
)

LONG_BODY = "\n".join(f"    step_{index}()" for index in range(25))
SHORT_BODY = "\n".join(f"    step_{index}()" for index in range(5))


class TestNoLongMethod(RuleTestCase):
    rule = NoLongMethod
    valid = [
        f"def load():\n{SHORT_BODY}",
        (f"def load():\n{LONG_BODY}", {"max_statements": 40}),
    ]
    invalid = [
        f"def load():\n{LONG_BODY}",
        (f"def load():\n{SHORT_BODY}", {"max_statements": 2}),
    ]


class TestNoLargeClass(RuleTestCase):
    rule = NoLargeClass
    valid = ["class Store:\n    def load(self):\n        return 1"]
    invalid = [
        "class Store:\n" + "\n".join(f"    def step_{index}(self):\n        return {index}" for index in range(12)),
        (
            "class Store:\n    def __init__(self):\n"
            + "\n".join(f"        self.field_{index} = {index}" for index in range(12)),
            {"max_attributes": 5},
        ),
    ]


class TestNoLongParameterList(RuleTestCase):
    rule = NoLongParameterList
    valid = [
        "def load(first, second, third, fourth):\n    return 1",
        "class Store:\n    def load(self, first, second, third, fourth):\n        return 1",
        ("def load(a, b, c, d, e, f):\n    return 1", {"max_parameters": 8}),
    ]
    invalid = ["def load(first, second, third, fourth, fifth):\n    return 1"]


class TestNoPrimitiveObsession(RuleTestCase):
    rule = NoPrimitiveObsession
    valid = [
        "def load(name: str, age: int, active: bool) -> None: ...",
        "def load(street: Street, city: City, code: PostalCode) -> None: ...",
    ]
    invalid = ["def load(street: str, city: str, code: str) -> None: ..."]


class TestNoDataClumps(RuleTestCase):
    rule = NoDataClumps
    valid = [
        "def save(street, city, code): ...\ndef load(key): ...",
        "def save(street, city): ...\ndef load(street, city): ...",
    ]
    invalid = ["def save(street, city, code): ...\ndef load(street, city, code): ..."]


class TestNoRefusedBequest(RuleTestCase):
    rule = NoRefusedBequest
    valid = [
        "class Square(Shape):\n    def area(self):\n        return self.side ** 2",
        "class Shape(ABC):\n    def area(self):\n        raise NotImplementedError",
    ]
    invalid = ["class Square(Shape):\n    def rotate(self):\n        raise NotImplementedError"]


class TestNoTypeCodeSwitch(RuleTestCase):
    rule = NoTypeCodeSwitch
    valid = [
        "if kind == 'a':\n    first()\nelif kind == 'b':\n    second()",
        "if kind == 'a':\n    first()\nelif other == 'b':\n    second()\nelif third == 'c':\n    third()",
    ]
    invalid = [
        "if kind == 'a':\n    first()\nelif kind == 'b':\n    second()\nelif kind == 'c':\n    third()",
        "match kind:\n    case 'a':\n        first()\n    case 'b':\n        second()\n    case 'c':\n        third()",
    ]


class TestNoTemporaryField(RuleTestCase):
    rule = NoTemporaryField
    valid = [
        "class Store:\n    def __init__(self):\n        self.rows = []\n    def load(self):\n        self.rows = [1]",
        "class Store:\n    rows: list = []\n    def load(self):\n        self.rows = [1]",
    ]
    invalid = ["class Store:\n    def __init__(self):\n        self.rows = []\n    def load(self):\n        self.cache = {}"]


class TestNoCommentedOutCode(RuleTestCase):
    rule = NoCommentedOutCode
    valid = [
        "# Load the rows the caller asked for.\nrows = load()",
        "rows = load()  # noqa: E501",
        "# TODO: rows = load_all()",
    ]
    invalid = ["# rows = load_all()\nrows = load()", "def load():\n    # return cached()\n    return fresh()"]


class TestNoDuplicateCode(RuleTestCase):
    rule = NoDuplicateCode
    valid = [
        "def first():\n    a()\n    b()\n    c()\n\ndef second():\n    a()\n    b()\n    d()",
        "def first():\n    a()\n\ndef second():\n    a()",
    ]
    invalid = ["def first():\n    a()\n    b()\n    c()\n\ndef second():\n    a()\n    b()\n    c()"]


class TestNoDataClass(RuleTestCase):
    rule = NoDataClass
    valid = [
        "@dataclass\nclass Row:\n    def __init__(self):\n        self.value = 1",
        "class Row:\n    def __init__(self):\n        self.value = 1\n    def total(self):\n        return self.value * 2",
        "class Row(NamedTuple):\n    def __init__(self):\n        self.value = 1",
    ]
    invalid = ["class Row:\n    def __init__(self, value):\n        self._value = value\n    def get_value(self):\n        return self._value"]


class TestNoUnreachableCode(RuleTestCase):
    rule = NoUnreachableCode
    valid = ["def load():\n    return 1", "def load():\n    if ready:\n        return 1\n    return 2"]
    invalid = ["def load():\n    return 1\n    log()", "for row in rows:\n    break\n    log()"]


class TestNoLazyClass(RuleTestCase):
    rule = NoLazyClass
    valid = [
        "class Store:\n    def __init__(self):\n        self.rows = []\n    def load(self):\n        return self.rows",
        "class Store:\n    def load(self):\n        return 1\n    def save(self):\n        return 2",
        "class Marker(Protocol):\n    def load(self):\n        ...",
    ]
    invalid = ["class Formatter:\n    def render(self, row):\n        return str(row)"]


class TestNoUnusedParameter(RuleTestCase):
    rule = NoUnusedParameter
    valid = [
        "def load(key):\n    return rows[key]",
        "def load(_key):\n    return rows",
        "def load(key):\n    ...",
    ]
    invalid = ["def load(key, cache):\n    return rows[key]"]


class TestNoFeatureEnvy(RuleTestCase):
    rule = NoFeatureEnvy
    valid = [
        "class Report:\n    def total(self, order):\n        return self.rate * order.amount",
        "class Report:\n    def total(self):\n        return self.a + self.b + self.c",
    ]
    invalid = [
        "class Report:\n    def total(self, order):\n"
        "        return order.amount + order.tax + order.shipping + order.discount + order.fee",
        (
            "class Report:\n    def total(self, order):\n        return order.amount + order.tax",
            {"min_accesses": 2},
        ),
    ]


class TestNoMessageChains(RuleTestCase):
    rule = NoMessageChains
    valid = [
        "value = order.customer.name",
        "value = self.rows.first",
        ("value = order.a.b.c.d", {"max_links": 6}),
    ]
    invalid = [
        "value = order.customer.address.city.name",
        "value = self.order.customer.address.city",
    ]


class TestNoMiddleMan(RuleTestCase):
    rule = NoMiddleMan
    valid = [
        "class Store:\n    def load(self):\n        return self.rows\n    def save(self, row):\n        self.rows.append(row)",
        "class Store:\n    def load(self):\n        return self.inner.load()",
    ]
    invalid = [
        "class Store:\n    def load(self):\n        return self.inner.load()\n    def save(self, row):\n        return self.inner.save(row)",
    ]


if __name__ == "__main__":
    unittest.main()
