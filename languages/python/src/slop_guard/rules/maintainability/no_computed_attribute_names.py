"""Reject building attribute or variable names at runtime."""

from __future__ import annotations

import ast

from ...rule import Rule

NAMESPACE_CALLS = frozenset({"globals", "locals", "vars"})


class NoComputedAttributeNames(Rule):
    name = "no-computed-attribute-names"
    group = "maintainability"
    reference = "https://docs.quantifiedcode.com/python-anti-patterns/maintainability/dynamically_creating_names.html"
    description = (
        "Disallow creating attribute or variable names at runtime with `setattr` or by writing "
        "into `globals()`."
    )

    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Name) and node.func.id == "setattr" and len(node.args) >= 2:
            name = node.args[1]
            if not (isinstance(name, ast.Constant) and isinstance(name.value, str)):
                owner = self.unparse(node.args[0])
                self.report(
                    node,
                    f"This builds an attribute name on `{owner}` at runtime, so no search finds "
                    f"where it is defined and no type checker knows it exists. Parse the incoming "
                    f"data into named fields, or keep it in a dictionary you read explicitly.",
                )
        self.generic_visit(node)

    def visit_Subscript(self, node: ast.Subscript) -> None:
        target = node.value
        if (
            isinstance(node.ctx, (ast.Store, ast.Del))
            and isinstance(target, ast.Call)
            and isinstance(target.func, ast.Name)
            and target.func.id in NAMESPACE_CALLS
        ):
            self.report(
                node,
                f"Writing into `{target.func.id}()` creates a name that no reader can find by "
                f"searching. Keep the value in a dictionary, or give it a real name.",
            )
        self.generic_visit(node)
