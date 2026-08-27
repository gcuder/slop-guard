"""Coverage for the rules that police type contracts."""

from __future__ import annotations

import unittest

from rule_tester import RuleTestCase
from slop_guard.rules.evidence import (
    NoAnyParameters,
    NoAnyReturns,
    NoAnyTypeAliases,
    NoObjectParameters,
    NoUnsafeDictionaryType,
)


class TestNoAnyParameters(RuleTestCase):
    rule = NoAnyParameters
    valid = [
        "def load(user: User) -> None: ...",
        "from typing import Any\ndef fail(cause: Any) -> None: ...",
        "def load(user) -> None: ...",
        "from typing import Any\ndef load(values: dict[str, Any]) -> None: ...",
        ("from typing import Any\ndef wrap(*args: Any, **kwargs: Any) -> None: ...", {"allow_variadic_any": True}),
    ]
    invalid = [
        "from typing import Any\ndef load(user: Any) -> None: ...",
        "import typing\ndef load(user: typing.Any) -> None: ...",
        "from typing import Any as Whatever\ndef load(user: Whatever) -> None: ...",
        "from typing import Any\nclass Store:\n    def put(self, value: Any) -> None: ...",
        "from typing import Any\ndef wrap(*args: Any) -> None: ...",
    ]


class TestNoAnyReturns(RuleTestCase):
    rule = NoAnyReturns
    valid = [
        "def load() -> User: ...",
        "def load(): ...",
        "from typing import Any\ndef load(value: Any) -> User: ...",
    ]
    invalid = [
        "from typing import Any\ndef load() -> Any: ...",
        "from typing import Any\nasync def load() -> Any: ...",
        "from typing import Any, Awaitable\ndef load() -> Awaitable[Any]: ...",
        "from typing import Any\ndef load() -> list[Any]: ...",
        "from typing import Any\ndef load() -> str | Any: ...",
        "from typing import Any, Callable\nhandler: Callable[[str], Any] = build()",
    ]


class TestNoAnyTypeAliases(RuleTestCase):
    rule = NoAnyTypeAliases
    valid = [
        "from typing import Any\nvalue: Any\n",
        "Payload = dict[str, str]",
    ]
    invalid = [
        "from typing import Any\nPayload = Any",
        "from typing import Any, TypeAlias\nPayload: TypeAlias = Any",
        "from typing import Any\ntype Payload = Any",
    ]


class TestNoObjectParameters(RuleTestCase):
    rule = NoObjectParameters
    valid = [
        "def save(value: User) -> None: ...",
        "def save(value) -> None: ...",
        "def save(value: list[object]) -> None: ...",
    ]
    invalid = [
        "def save(value: object) -> None: ...",
        "class Store:\n    def save(self, value: object) -> None: ...",
    ]


class TestNoUnsafeDictionaryType(RuleTestCase):
    rule = NoUnsafeDictionaryType
    valid = [
        "metadata: dict[str, str] = {}",
        "def load(rows: dict[str, Row]) -> None: ...",
        "from typing import Mapping\ndef load(rows: Mapping[str, Row]) -> None: ...",
    ]
    invalid = [
        "from typing import Any\nmetadata: dict[str, Any] = {}",
        "metadata: dict[str, object] = {}",
        "from typing import Any, Mapping\ndef load(rows: Mapping[str, Any]) -> None: ...",
        "from typing import Any\ndef load() -> dict[str, Any]: ...",
        "def load(rows: dict) -> None: ...",
    ]


if __name__ == "__main__":
    unittest.main()
