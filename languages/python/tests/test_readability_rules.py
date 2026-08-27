"""Coverage for the readability rules."""

from __future__ import annotations

import unittest

from rule_tester import RuleTestCase
from slop_guard.rules.readability import (
    NoCamelCaseFunctions,
    NoComparisonToBool,
    NoComparisonToNone,
    NoIdentityComparisonToLiteral,
    NoTypeComparison,
    NoTypeInName,
    PreferComprehensionOverMapFilter,
    PreferDictComprehension,
    PreferDictItems,
    PreferEafpForFiles,
    PreferEnumerate,
    PreferFormatMapping,
    PreferNamedTuple,
    PreferTupleSwap,
    PreferZip,
)


class TestPreferEafpForFiles(RuleTestCase):
    rule = PreferEafpForFiles
    valid = [
        "try:\n    os.unlink('rows.csv')\nexcept OSError:\n    log()",
        "if os.path.exists('rows.csv'):\n    report()",
    ]
    invalid = [
        "if os.path.exists('rows.csv'):\n    os.unlink('rows.csv')",
        "if not os.path.isfile(name):\n    open(name)",
    ]


class TestNoComparisonToNone(RuleTestCase):
    rule = NoComparisonToNone
    valid = ["if value is None:\n    stop()", "if value is not None:\n    stop()"]
    invalid = ["if value == None:\n    stop()", "if value != None:\n    stop()"]


class TestNoComparisonToBool(RuleTestCase):
    rule = NoComparisonToBool
    valid = [
        "if ready:\n    stop()",
        "if not ready:\n    stop()",
        "if ready is False:\n    stop()",  # `is` distinguishes False from 0
    ]
    invalid = ["if ready == True:\n    stop()", "if ready != False:\n    stop()"]


class TestNoTypeComparison(RuleTestCase):
    rule = NoTypeComparison
    valid = ["if isinstance(value, str):\n    stop()", "value = type(other)"]
    invalid = ["if type(value) == type(other):\n    stop()", "if type(value) is str:\n    stop()"]


class TestPreferDictComprehension(RuleTestCase):
    rule = PreferDictComprehension
    valid = ["index = {row.id: row for row in rows}", "index = dict(rows)"]
    invalid = ["index = dict((row.id, row) for row in rows)", "index = dict([(k, v) for k, v in pairs])"]


class TestPreferFormatMapping(RuleTestCase):
    rule = PreferFormatMapping
    valid = [
        "'{first} {last}'.format(**person)",
        "'{0}'.format(person['first'])",
    ]
    invalid = ["'{0} {1}'.format(person['first'], person['last'])"]


class TestPreferDictItems(RuleTestCase):
    rule = PreferDictItems
    valid = [
        "for key, value in rows.items():\n    use(key, value)",
        "for key in rows:\n    use(key)",
    ]
    invalid = ["for key in rows:\n    use(rows[key])"]


class TestPreferNamedTuple(RuleTestCase):
    rule = PreferNamedTuple
    valid = [
        "def load():\n    return first, last",
        "def load():\n    return Name(first, middle, last)",
    ]
    invalid = ["def load():\n    return first, middle, last"]


class TestPreferTupleSwap(RuleTestCase):
    rule = PreferTupleSwap
    valid = ["a, b = b, a % b", "temp = b\nuse(temp)"]
    invalid = ["def gcd():\n    temp = b\n    b = a % b\n    a = temp"]


class TestPreferZip(RuleTestCase):
    rule = PreferZip
    valid = ["for left, right in zip(names, ages):\n    use(left, right)"]
    invalid = ["for i in range(len(names)):\n    use(names[i], ages[i])"]


class TestNoTypeInName(RuleTestCase):
    rule = NoTypeInName
    valid = ["count = 0", "def load(rows):\n    return rows", "interior = 1"]
    invalid = ["count_int = 'hello'", "def load(rows_list):\n    return rows_list", "str_name = 1"]


class TestNoIdentityComparisonToLiteral(RuleTestCase):
    rule = NoIdentityComparisonToLiteral
    valid = ["if value is None:\n    stop()", "if value == 'ready':\n    stop()"]
    invalid = ["if value is 'ready':\n    stop()", "if count is 5:\n    stop()"]


class TestPreferEnumerate(RuleTestCase):
    rule = PreferEnumerate
    valid = ["for index, row in enumerate(rows):\n    use(index, row)", "for row in rows:\n    use(row)"]
    invalid = ["for i in range(len(rows)):\n    use(rows[i])", "for i in range(0, len(rows)):\n    use(i)"]


class TestPreferComprehensionOverMapFilter(RuleTestCase):
    rule = PreferComprehensionOverMapFilter
    valid = ["[value * 2 for value in values]", "map(str, values)"]
    invalid = ["map(lambda value: value * 2, values)", "filter(lambda value: value > 2, values)"]


class TestNoCamelCaseFunctions(RuleTestCase):
    rule = NoCamelCaseFunctions
    valid = ["def load_rows():\n    pass", "def load():\n    pass"]
    invalid = ["def loadRows():\n    pass", "def parseHttpResponse():\n    pass"]


if __name__ == "__main__":
    unittest.main()
