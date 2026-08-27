"""Base class every slop-guard rule extends."""

from __future__ import annotations

import ast
from typing import ClassVar, Mapping

from .diagnostics import Diagnostic, position
from .imports import ImportIndex
from .source import SourceFile

ANY_PATHS = ("typing.Any", "typing_extensions.Any", "t.Any")
CAST_PATHS = ("typing.cast", "typing_extensions.cast")
MAPPING_PATHS = (
    "dict",
    "typing.Dict",
    "typing.Mapping",
    "typing.MutableMapping",
    "typing.DefaultDict",
    "typing.OrderedDict",
    "collections.OrderedDict",
    "collections.defaultdict",
    "collections.abc.Mapping",
    "collections.abc.MutableMapping",
)
TYPE_GUARD_PATHS = (
    "typing.TypeGuard",
    "typing.TypeIs",
    "typing_extensions.TypeGuard",
    "typing_extensions.TypeIs",
)

FunctionNode = ast.FunctionDef | ast.AsyncFunctionDef


class TypePredicates(ast.NodeVisitor):
    """The type questions rules ask about annotations, kept apart from rule mechanics."""

    imports: ImportIndex

    def is_any(self, node: ast.expr | None) -> bool:
        return self.imports.matches(node, *ANY_PATHS)

    def is_object(self, node: ast.expr | None) -> bool:
        return isinstance(node, ast.Name) and node.id == "object" and "object" not in self.imports.symbols

    def is_cast_call(self, node: ast.AST) -> bool:
        return isinstance(node, ast.Call) and self.imports.matches(node.func, *CAST_PATHS)

    def contains_any(self, node: ast.expr | None) -> ast.expr | None:
        """Return the first `Any` node inside a type expression, if there is one."""
        if node is None:
            return None
        if self.is_any(node):
            return node
        for child in ast.walk(node):
            if child is node:
                continue
            if isinstance(child, ast.expr) and self.is_any(child):
                return child
        return None


class Rule(TypePredicates):
    """A single check over one parsed module.

    `group` places the rule in a selectable set, and `reference` links the pattern it enforces to
    the source that describes it.
    """

    name: ClassVar[str]
    description: ClassVar[str]
    group: ClassVar[str] = "evidence"
    reference: ClassVar[str] = ""

    def __init__(self, source: SourceFile, options: Mapping[str, object] | None = None) -> None:
        self.source = source
        self.options: Mapping[str, object] = options or {}
        self.imports = ImportIndex.build(source.tree)
        self.diagnostics: list[Diagnostic] = []

    def run(self) -> list[Diagnostic]:
        self.visit(self.source.tree)
        return self.diagnostics

    def report(self, node: ast.AST, message: str) -> None:
        line, column = position(node)
        self.diagnostics.append(
            Diagnostic(
                rule=self.name,
                message=message,
                line=line,
                column=column,
                path=self.source.path,
            )
        )

    def option(self, key: str, default: object) -> object:
        return self.options.get(key, default)

    def flag(self, key: str, *, default: bool = False) -> bool:
        value = self.option(key, default)
        return bool(value)

    def threshold(self, key: str, default: int) -> int:
        """Read a numeric option, falling back to the rule's default when it is not a number."""
        value = self.option(key, default)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return default
        return int(value)

    @staticmethod
    def parameters(node: FunctionNode | ast.Lambda) -> list[ast.arg]:
        args = node.args
        collected = [*args.posonlyargs, *args.args, *args.kwonlyargs]
        if args.vararg is not None:
            collected.append(args.vararg)
        if args.kwarg is not None:
            collected.append(args.kwarg)
        return collected

    @staticmethod
    def variadic_parameters(node: FunctionNode | ast.Lambda) -> set[str]:
        args = node.args
        names = set()
        if args.vararg is not None:
            names.add(args.vararg.arg)
        if args.kwarg is not None:
            names.add(args.kwarg.arg)
        return names

    @staticmethod
    def unparse(node: ast.AST) -> str:
        return ast.unparse(node)
