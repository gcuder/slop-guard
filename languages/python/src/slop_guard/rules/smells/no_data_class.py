"""Reject classes that hold data and do nothing with it."""

from __future__ import annotations

import ast

from ...rule import FunctionNode, Rule

DATA_BASES = frozenset(
    {"NamedTuple", "TypedDict", "BaseModel", "Enum", "IntEnum", "StrEnum", "Flag", "Protocol", "Exception"}
)
DATA_DECORATORS = ("dataclass", "attrs", "define", "frozen", "model")


class NoDataClass(Rule):
    name = "no-data-class"
    group = "smells"
    reference = "https://refactoring.guru/smells/data-class"
    description = (
        "Disallow a class whose methods only store and return its own fields, unless it is declared "
        "as a data container."
    )

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        if self._is_declared_container(node):
            self.generic_visit(node)
            return
        methods = [
            statement
            for statement in node.body
            if isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]
        behaviour = [
            method
            for method in methods
            if method.name != "__init__" and not self._is_accessor(method)
        ]
        has_state = any(
            isinstance(child, ast.Attribute)
            and isinstance(child.ctx, ast.Store)
            and isinstance(child.value, ast.Name)
            and child.value.id == "self"
            for child in ast.walk(node)
        )
        if has_state and methods and not behaviour:
            self.report(
                node,
                f"`{node.name}` only stores and hands back its own fields, so the code that "
                f"decides anything about that data lives somewhere else. Move the behaviour that "
                f"reads these fields into the class, or declare it a `dataclass` and let it be "
                f"plain data.",
            )
        self.generic_visit(node)

    def _is_declared_container(self, node: ast.ClassDef) -> bool:
        for decorator in node.decorator_list:
            text = self.unparse(decorator)
            if any(marker in text for marker in DATA_DECORATORS):
                return True
        return any(self.unparse(base).split("[")[0].split(".")[-1] in DATA_BASES for base in node.bases)

    def _is_accessor(self, method: FunctionNode) -> bool:
        if any("property" in self.unparse(decorator) for decorator in method.decorator_list):
            return True
        if method.name.startswith("__") and method.name.endswith("__"):
            return True
        body = [statement for statement in method.body if not self._is_docstring(statement)]
        if len(body) != 1:
            return False
        only = body[0]
        if isinstance(only, ast.Return) and isinstance(only.value, ast.Attribute):
            return True
        return isinstance(only, ast.Assign) and all(
            isinstance(target, ast.Attribute) for target in only.targets
        )

    @staticmethod
    def _is_docstring(statement: ast.stmt) -> bool:
        return (
            isinstance(statement, ast.Expr)
            and isinstance(statement.value, ast.Constant)
            and isinstance(statement.value.value, str)
        )
