"""Reject indentation that mixes tabs and spaces."""

from __future__ import annotations

from ...diagnostics import Diagnostic
from ...rule import Rule


class NoMixedIndentation(Rule):
    name = "no-mixed-indentation"
    group = "correctness"
    reference = "https://docs.quantifiedcode.com/python-anti-patterns/correctness/indentation_contains_mixed_spaces_and_tabs.html"
    description = "Disallow indentation that mixes tabs and spaces within one file."

    def run(self) -> list[Diagnostic]:
        seen: set[str] = set()
        for number, line in enumerate(self.source.lines, start=1):
            indentation = line[: len(line) - len(line.lstrip())]
            if not indentation:
                continue
            if "\t" in indentation and " " in indentation:
                self._report(number, indentation, "This line mixes tabs and spaces in its indentation")
                continue
            seen.add("tab" if "\t" in indentation else "space")
            if len(seen) > 1:
                self._report(
                    number,
                    indentation,
                    "This line is indented differently from earlier lines in the same file",
                )
                seen = {"tab" if "\t" in indentation else "space"}
        return self.diagnostics

    def _report(self, line: int, indentation: str, opening: str) -> None:
        self.diagnostics.append(
            Diagnostic(
                rule=self.name,
                message=(
                    f"{opening}, so what the interpreter sees and what the reader sees can differ. "
                    f"Indent the whole file with four spaces."
                ),
                line=line,
                column=len(indentation),
                path=self.source.path,
            )
        )
