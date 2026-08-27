"""Reject classes that do not earn their keep."""

from __future__ import annotations

import ast

from ...rule import Rule

EXEMPT_BASES = frozenset({"Protocol", "ABC", "Enum", "IntEnum", "StrEnum", "Exception", "TypedDict", "NamedTuple"})


class NoLazyClass(Rule):
    name = "no-lazy-class"
    group = "smells"
    reference = "https://refactoring.guru/smells/lazy-class"
    description = "Disallow a class with no state and at most one method; a function says the same thing."

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        if node.decorator_list or any(
            self.unparse(base).split("[")[0].split(".")[-1] in EXEMPT_BASES for base in node.bases
        ):
            self.generic_visit(node)
            return
        methods = [
            statement
            for statement in node.body
            if isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef))
            and not (statement.name.startswith("__") and statement.name.endswith("__"))
        ]
        has_state = any(
            isinstance(child, ast.Attribute)
            and isinstance(child.ctx, ast.Store)
            and isinstance(child.value, ast.Name)
            and child.value.id == "self"
            for child in ast.walk(node)
        )
        fields = [statement for statement in node.body if isinstance(statement, (ast.Assign, ast.AnnAssign))]
        if not has_state and not fields and len(methods) <= 1 and methods:
            self.report(
                node,
                f"`{node.name}` holds no state and has one method, so the class adds a name and a "
                f"call without adding a decision. Make `{methods[0].name}` a function.",
            )
        self.generic_visit(node)
