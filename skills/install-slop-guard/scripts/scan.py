#!/usr/bin/env python3
"""Run the bundled Python checker over a repository without installing anything.

The rules live in this skill's assets, so a scan needs no copy in the target project and changes
no files. Takes the same flags as the installed checker: paths, `--select`, `--ignore`,
`--format json`, `--exit-zero`, `--list-rules`.
"""

from __future__ import annotations

import sys
from pathlib import Path

ASSETS = Path(__file__).resolve().parent.parent / "assets"

if not (ASSETS / "python").is_dir():
    print(f"This skill has no bundled Python checker at {ASSETS / 'python'}.", file=sys.stderr)
    raise SystemExit(1)

sys.path.insert(0, str(ASSETS))

from python.cli import main  # noqa: E402 - the path above makes this importable

raise SystemExit(main(sys.argv[1:]))
