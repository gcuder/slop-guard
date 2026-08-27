"""Reject string-keyed attribute access where a real attribute exists."""

from __future__ import annotations

import ast

from ...rule import Rule

DYNAMIC_BUILTINS = {"getattr": "read", "setattr": "write", "hasattr": "probe", "delattr": "delete"}


class NoDynamicAttributeAccess(Rule):
    name = "no-dynamic-attribute-access"
    group = "evidence"
    description = (
        "Disallow `getattr`, `setattr`, `hasattr`, and `delattr` with a literal name; use the "
        "attribute directly or parse the object first."
    )

    def visit_Call(self, node: ast.Call) -> None:
        function = node.func
        if isinstance(function, ast.Name) and function.id in DYNAMIC_BUILTINS and len(node.args) >= 2:
            name = node.args[1]
            if isinstance(name, ast.Constant) and isinstance(name.value, str):
                owner = self.unparse(node.args[0])
                self.report(
                    node,
                    f"`{function.id}({owner}, \"{name.value}\")` hides a plain attribute behind a "
                    f"string, so no type checker sees it. Write `{owner}.{name.value}`, or parse "
                    f"the object into a type that declares the attribute.",
                )
        self.generic_visit(node)

    def visit_Subscript(self, node: ast.Subscript) -> None:
        if (
            isinstance(node.value, ast.Attribute)
            and node.value.attr == "__dict__"
            and isinstance(node.slice, ast.Constant)
        ):
            self.report(
                node,
                "Reaching into `__dict__` bypasses the declared interface of the object. Use the "
                "attribute directly, or parse the object into a type that declares it.",
            )
        self.generic_visit(node)
