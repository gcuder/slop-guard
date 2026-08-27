"""Coverage for the rules that police casts, widening, and runtime probing."""

from __future__ import annotations

import unittest

from rule_tester import RuleTestCase
from slop_guard.rules.evidence import (
    NoChainedCasts,
    NoConditionalEmptyDictSpread,
    NoDynamicAttributeAccess,
    NoKnownValueWidening,
    NoRuntimeIsinstance,
    NoWidenThenCast,
    RequireSafetyCommentForCast,
)


class TestNoChainedCasts(RuleTestCase):
    rule = NoChainedCasts
    valid = [
        "from typing import cast\nuser = cast(User, payload)",
        "user = build(User, payload)",
    ]
    invalid = [
        "from typing import cast\nuser = cast(User, cast(object, payload))",
        "import typing\nuser = typing.cast(User, typing.cast(typing.Any, payload))",
    ]


class TestRequireSafetyCommentForCast(RuleTestCase):
    rule = RequireSafetyCommentForCast
    valid = [
        "from typing import cast\n# SAFETY: parse_user_id validated the identifier already.\nuser_id = cast(UserId, value)",
        "from typing import cast\nuser_id = cast(UserId, value)  # SAFETY: validated upstream.",
        "user_id = build(value)",
    ]
    invalid = [
        "from typing import cast\nuser_id = cast(UserId, value)",
        "from typing import cast\n# TODO: tidy up\nuser_id = cast(UserId, value)",
    ]


class TestNoWidenThenCast(RuleTestCase):
    rule = NoWidenThenCast
    valid = [
        "from typing import cast\nuser = load()\nstored = cast(User, payload)",
        "from typing import Any, cast\ndef run() -> None:\n    payload: Any = receive()\n    user = parse(payload)",
    ]
    invalid = [
        "from typing import Any, cast\ndef run() -> None:\n    stored: Any = load_user()\n    user = cast(User, stored)",
        "from typing import cast\ndef run() -> None:\n    stored: object = load_user()\n    user = cast(User, stored)",
        "from typing import Any, cast\ndef run() -> None:\n    stored = cast(Any, load_user())\n    user = cast(User, stored)",
    ]


class TestNoKnownValueWidening(RuleTestCase):
    rule = NoKnownValueWidening
    valid = [
        "handlers = {'start': start_handler}",
        "handlers: Final = {'start': start_handler}",
        "counts: dict[str, int] = {}",
        "rows: dict[UserId, Row] = load_rows()",
    ]
    invalid = [
        "from typing import Any\npayload: Any = load_user()",
        "user: object = load_user()",
        "handlers: dict[str, Handler] = {'start': start_handler}",
    ]


class TestNoConditionalEmptyDictSpread(RuleTestCase):
    rule = NoConditionalEmptyDictSpread
    valid = [
        "options = {'timeout': timeout}",
        "options = {**defaults, 'timeout': timeout}",
        "options = {'timeout': timeout if timeout is not None else DEFAULT_TIMEOUT}",
    ]
    invalid = [
        "options = {**({'timeout': timeout} if timeout is not None else {})}",
        "options = {**({} if timeout is None else {'timeout': timeout})}",
        "options = dict(**({'timeout': timeout} if timeout else {}))",
    ]


class TestNoRuntimeIsinstance(RuleTestCase):
    rule = NoRuntimeIsinstance
    valid = [
        "user = parse_user(payload)",
        (
            "from typing import TypeGuard\ndef is_user(value: object) -> TypeGuard[User]:\n"
            "    return isinstance(value, User)",
            {"allow_in_type_guards": True},
        ),
    ]
    valid = [*valid, "if type(payload) is str:\n    use_name(payload)"]  # no-type-comparison owns this
    invalid = [
        "if isinstance(payload, str):\n    use_name(payload)",
        "from typing import TypeGuard\ndef is_user(value: object) -> TypeGuard[User]:\n    return isinstance(value, User)",
    ]


class TestNoDynamicAttributeAccess(RuleTestCase):
    rule = NoDynamicAttributeAccess
    valid = [
        "value = owner.name",
        "value = getattr(owner, key)",
        "value = owner.registry['name']",
    ]
    invalid = [
        "value = getattr(owner, 'name')",
        "setattr(owner, 'name', value)",
        "if hasattr(owner, 'name'):\n    use(owner)",
        "value = owner.__dict__['name']",
    ]


if __name__ == "__main__":
    unittest.main()
