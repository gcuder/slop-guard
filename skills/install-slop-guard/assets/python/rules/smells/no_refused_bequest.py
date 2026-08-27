"""Reject subclasses that inherit a method only to refuse it."""

from __future__ import annotations

import ast

from ...rule import FunctionNode, Rule

ABSTRACT_BASES = frozenset({"ABC", "ABCMeta", "Protocol"})


class NoRefusedBequest(Rule):
    name = "no-refused-bequest"
    group = "smells"
    reference = "https://refactoring.guru/smells/refused-bequest"
    description = "Disallow overriding an inherited method with `raise NotImplementedError`."

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        if not node.bases or self._is_abstract(node):
            self.generic_visit(node)
            return
        for statement in node.body:
            if isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef)) and self._refuses(statement):
                base = self.unparse(node.bases[0])
                self.report(
                    statement,
                    f"`{node.name}` inherits `{statement.name}` from `{base}` and then refuses "
                    f"it, so it is not the thing its base class promises. Take what you need by "
                    f"holding a `{base}` instead of inheriting from it.",
                )
        self.generic_visit(node)

    def _is_abstract(self, node: ast.ClassDef) -> bool:
        if any(self.unparse(base).split(".")[-1] in ABSTRACT_BASES for base in node.bases):
            return True
        return any(
            self.unparse(keyword.value).split(".")[-1] in ABSTRACT_BASES
            for keyword in node.keywords
            if keyword.arg == "metaclass"
        )

    def _refuses(self, node: FunctionNode) -> bool:
        if any("abstract" in self.unparse(decorator) for decorator in node.decorator_list):
            return False
        body = [
            statement
            for statement in node.body
            if not (
                isinstance(statement, ast.Expr)
                and isinstance(statement.value, ast.Constant)
                and isinstance(statement.value.value, str)
            )
        ]
        if len(body) != 1 or not isinstance(body[0], ast.Raise):
            return False
        raised = body[0].exc
        name = self.unparse(raised) if raised is not None else ""
        return name.split("(")[0].split(".")[-1] == "NotImplementedError"
