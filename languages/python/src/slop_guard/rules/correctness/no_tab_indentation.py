"""Reject tab-indented source."""

from __future__ import annotations

from ...diagnostics import Diagnostic
from ...rule import Rule


class NoTabIndentation(Rule):
    name = "no-tab-indentation"
    group = "correctness"
    reference = "https://docs.quantifiedcode.com/python-anti-patterns/correctness/indentation_contains_tabs.html"
    description = "Disallow tabs in indentation; PEP 8 indents with four spaces."

    def run(self) -> list[Diagnostic]:
        for number, line in enumerate(self.source.lines, start=1):
            indentation = line[: len(line) - len(line.lstrip())]
            if "\t" in indentation:
                self.diagnostics.append(
                    Diagnostic(
                        rule=self.name,
                        message=(
                            "This line is indented with a tab, so its width depends on the reader's "
                            "editor. Indent with four spaces, as PEP 8 asks."
                        ),
                        line=number,
                        column=indentation.index("\t") + 1,
                        path=self.source.path,
                    )
                )
        return self.diagnostics
