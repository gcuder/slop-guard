"""Configuration read from `[tool.slop-guard]` in pyproject.toml."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path

DEFAULT_EXCLUDE = (
    ".agent",
    ".agents",
    ".claude",
    ".codex",
    ".continue",
    ".cursor",
    ".gemini",
    ".git",
    ".opencode",
    ".pi",
    ".roo",
    ".venv",
    ".windsurf",
    "__pycache__",
    "build",
    "dist",
    "node_modules",
    "venv",
)


@dataclass(frozen=True, slots=True)
class Config:
    """Resolved settings for one run."""

    select: tuple[str, ...] | None = None
    ignore: tuple[str, ...] = ()
    exclude: tuple[str, ...] = DEFAULT_EXCLUDE
    rules: dict[str, dict[str, object]] = field(default_factory=dict)

    @classmethod
    def load(cls, path: Path | None) -> "Config":
        """Read configuration from a pyproject.toml, or return defaults."""
        if path is None or not path.is_file():
            return cls()
        with path.open("rb") as handle:
            document = tomllib.load(handle)
        section = document.get("tool", {}).get("slop-guard", {})
        if not isinstance(section, dict):
            return cls()
        rules = section.get("rules", {})
        return cls(
            select=cls._names(section.get("select")),
            ignore=cls._names(section.get("ignore")) or (),
            exclude=cls._names(section.get("exclude")) or DEFAULT_EXCLUDE,
            rules={name: dict(values) for name, values in rules.items() if isinstance(values, dict)},
        )

    @staticmethod
    def _names(value: object) -> tuple[str, ...] | None:
        if isinstance(value, (list, tuple)) and value:
            return tuple(str(item) for item in value)
        return None


def find_pyproject(start: Path) -> Path | None:
    """Walk upward from a path looking for the nearest pyproject.toml."""
    current = start.resolve()
    if current.is_file():
        current = current.parent
    for directory in [current, *current.parents]:
        candidate = directory / "pyproject.toml"
        if candidate.is_file():
            return candidate
    return None
