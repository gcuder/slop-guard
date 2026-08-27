"""Coverage for rule selection, configuration, and the command line."""

from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from slop_guard import check_source, rule_names, selected_rules
from slop_guard.cli import collect_files, main
from slop_guard.config import Config
from slop_guard.source import SourceFile

SLOP = "from typing import Any\n\n\ndef load(user: Any) -> Any:\n    return user\n"


class TestRegistry(unittest.TestCase):
    def test_every_rule_is_registered_once(self) -> None:
        names = rule_names()
        self.assertEqual(len(names), len(set(names)))
        self.assertIn("no-any-parameters", names)

    def test_unknown_rule_is_rejected(self) -> None:
        with self.assertRaises(KeyError):
            selected_rules(["no-such-rule"], None)

    def test_ignore_removes_a_rule(self) -> None:
        rules = selected_rules(None, ["no-any-parameters"])
        self.assertNotIn("no-any-parameters", [rule.name for rule in rules])

    def test_findings_are_sorted_by_position(self) -> None:
        findings = check_source(SourceFile.parse(SLOP))
        self.assertTrue(findings)
        positions = [(finding.line, finding.column) for finding in findings]
        self.assertEqual(positions, sorted(positions))


class TestConfig(unittest.TestCase):
    def test_reads_the_tool_section(self) -> None:
        with TemporaryDirectory() as directory:
            path = Path(directory) / "pyproject.toml"
            path.write_text(
                '[tool.slop-guard]\nignore = ["no-any-returns"]\n\n'
                '[tool.slop-guard.rules."no-runtime-isinstance"]\nallow_in_type_guards = true\n',
                encoding="utf-8",
            )
            config = Config.load(path)
        self.assertEqual(config.ignore, ("no-any-returns",))
        self.assertEqual(config.rules["no-runtime-isinstance"], {"allow_in_type_guards": True})

    def test_missing_file_gives_defaults(self) -> None:
        config = Config.load(None)
        self.assertIsNone(config.select)
        self.assertIn(".venv", config.exclude)


class TestCommandLine(unittest.TestCase):
    def test_reports_findings_and_exits_non_zero(self) -> None:
        with TemporaryDirectory() as directory:
            path = Path(directory) / "module.py"
            path.write_text(SLOP, encoding="utf-8")
            self.assertEqual(main([str(path), "--format", "json"]), 1)
            self.assertEqual(main([str(path), "--exit-zero"]), 0)
            self.assertEqual(main([str(path), "--ignore", ",".join(rule_names())]), 0)

    def test_clean_source_exits_zero(self) -> None:
        with TemporaryDirectory() as directory:
            path = Path(directory) / "module.py"
            path.write_text("def load(user: User) -> User:\n    return user\n", encoding="utf-8")
            self.assertEqual(main([str(path)]), 0)

    def test_excluded_directories_are_skipped(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / ".venv").mkdir()
            (root / ".venv" / "vendored.py").write_text(SLOP, encoding="utf-8")
            (root / "app.py").write_text(SLOP, encoding="utf-8")
            files = collect_files([str(root)], Config().exclude)
        self.assertEqual([path.name for path in files], ["app.py"])


if __name__ == "__main__":
    unittest.main()
