"""Language detection shared by the installer and the scanner."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
REGISTRY = json.loads((SKILL_ROOT / "languages.json").read_text(encoding="utf-8"))
FILE_LIMIT = 20000


@dataclass(frozen=True, slots=True)
class Detection:
    """One language the repository appears to contain."""

    language: dict
    markers: tuple[str, ...]
    sources: int


def _source_extensions(root: Path, excluded: set[str]) -> list[str]:
    found: list[str] = []
    queue = [root]
    while queue and len(found) < FILE_LIMIT:
        directory = queue.pop(0)
        try:
            entries = sorted(directory.iterdir())
        except OSError:
            continue
        for entry in entries:
            if entry.is_dir():
                if entry.name not in excluded:
                    queue.append(entry)
            elif len(found) < FILE_LIMIT:
                found.append(entry.suffix)
    return found


def detect(root: Path) -> list[Detection]:
    """Report which registered languages a directory appears to contain."""
    excluded = set(REGISTRY["exclude"])
    extensions = _source_extensions(root, excluded)
    results: list[Detection] = []
    for language in REGISTRY["languages"]:
        markers = tuple(name for name in language["markers"] if (root / name).exists())
        sources = sum(1 for suffix in extensions if suffix in language["extensions"])
        if markers or sources:
            results.append(Detection(language=language, markers=markers, sources=sources))
    return sorted(results, key=lambda result: result.sources, reverse=True)


def language(identifier: str) -> dict:
    """Look up one language by its id, or raise with the ids this skill knows."""
    for entry in REGISTRY["languages"]:
        if entry["id"] == identifier:
            return entry
    known = ", ".join(entry["id"] for entry in REGISTRY["languages"])
    raise KeyError(f"Unknown language {identifier}. This skill supports: {known}.")
