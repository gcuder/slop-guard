"""Reject `from module import *`."""

from __future__ import annotations

import ast

from ...rule import Rule


class NoWildcardImports(Rule):
    name = "no-wildcard-imports"
    group = "maintainability"
    reference = "https://docs.quantifiedcode.com/python-anti-patterns/maintainability/from_module_import_all_used.html"
    description = "Disallow `from module import *`, which hides where each name comes from."

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if any(alias.name == "*" for alias in node.names):
            module = node.module or "."
            self.report(
                node,
                f"`from {module} import *` puts an unknown set of names into this module, so a "
                f"reader cannot tell what came from where, and a new name in {module} can silently "
                f"shadow a local one. Import the names you use.",
            )
        self.generic_visit(node)
