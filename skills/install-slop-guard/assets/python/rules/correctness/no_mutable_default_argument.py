"""Reject mutable default argument values."""

from __future__ import annotations

import ast

from ...rule import FunctionNode, Rule

MUTABLE_CALLS = frozenset({"list", "dict", "set", "bytearray", "collections.OrderedDict", "collections.defaultdict"})


class NoMutableDefaultArgument(Rule):
    name = "no-mutable-default-argument"
    group = "correctness"
    reference = "https://docs.quantifiedcode.com/python-anti-patterns/correctness/mutable_default_value_as_argument.html"
    description = "Disallow mutable default argument values, which persist between calls."

    def visit_FunctionDef(self, node: FunctionNode) -> None:
        defaults = [*node.args.defaults, *[value for value in node.args.kw_defaults if value is not None]]
        for default in defaults:
            if self._is_mutable(default):
                self.report(
                    default,
                    f"`{self.unparse(default)}` is created once, when the function is defined, so "
                    f"every call shares and mutates the same object. Default to `None` and build "
                    f"the value inside the function.",
                )
        self.generic_visit(node)

    visit_AsyncFunctionDef = visit_FunctionDef

    def _is_mutable(self, node: ast.expr) -> bool:
        if isinstance(node, (ast.List, ast.Dict, ast.Set, ast.ListComp, ast.DictComp, ast.SetComp)):
            return True
        return isinstance(node, ast.Call) and self.imports.matches(node.func, *MUTABLE_CALLS)
