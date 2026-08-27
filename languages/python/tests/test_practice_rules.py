"""Coverage for the rules that police tests, naming, and error handling."""

from __future__ import annotations

import unittest

from rule_tester import RuleTestCase
from slop_guard.rules.evidence import (
    NoForbiddenTermsInSymbolNames,
    NoModuleMocking,
    NoSilentExceptionSwallow,
)


class TestNoModuleMocking(RuleTestCase):
    rule = NoModuleMocking
    valid = [
        "store = FakeUserStore()\nservice = UserService(store)",
        "monkeypatch.chdir(tmp_path)",
    ]
    invalid = [
        "from unittest import mock\nwith mock.patch('app.user_store.load'):\n    run()",
        "from unittest.mock import patch\n@patch('app.user_store.load')\ndef test_load(loader):\n    run()",
        "def test_load(mocker):\n    mocker.patch('app.user_store.load')",
        "def test_load(monkeypatch):\n    monkeypatch.setattr('app.user_store.load', fake_load)",
    ]


class TestNoForbiddenTermsInSymbolNames(RuleTestCase):
    rule = NoForbiddenTermsInSymbolNames
    valid = [
        "class User:\n    pass",
        "def load_user() -> User: ...",
        "dimensions = image.shape",
        ("class Payload:\n    pass", {"terms": ["shape"]}),
    ]
    invalid = [
        "class UserShape:\n    pass",
        "def build_shape() -> None: ...",
        "user_shape = build()",
        "def save(shape: User) -> None: ...",
        ("payload_data = build()", {"terms": ["data"]}),
    ]


class TestNoSilentExceptionSwallow(RuleTestCase):
    rule = NoSilentExceptionSwallow
    valid = [
        "try:\n    run()\nexcept TimeoutError:\n    retry()",
        "try:\n    run()\nexcept TimeoutError as error:\n    raise RunFailed() from error",
        "try:\n    run()\nexcept TimeoutError:\n    logger.warning('timed out')\n    raise",
    ]
    valid = [*valid, "try:\n    run()\nexcept:\n    handle()"]  # no-bare-except owns this
    invalid = [
        "try:\n    run()\nexcept Exception:\n    pass",
        "try:\n    run()\nexcept TimeoutError:\n    ...",
    ]


if __name__ == "__main__":
    unittest.main()
