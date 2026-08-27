"""Reject except clauses that a broader earlier clause already caught."""

from __future__ import annotations

import ast
import builtins

from ...rule import Rule


def _ancestors(name: str) -> tuple[str, ...]:
    exception = getattr(builtins, name, None)
    if isinstance(exception, type) and issubclass(exception, BaseException):
        return tuple(parent.__name__ for parent in exception.__mro__)
    return ()


class NoUnreachableExceptClause(Rule):
    name = "no-unreachable-except-clause"
    group = "correctness"
    reference = "https://docs.quantifiedcode.com/python-anti-patterns/correctness/bad_except_clauses_order.html"
    description = "Disallow an `except` clause that an earlier, broader clause already catches."

    def visit_Try(self, node: ast.Try) -> None:
        caught: list[str] = []
        for handler in node.handlers:
            names = self._names(handler.type)
            for name in names:
                shadow = next((earlier for earlier in caught if earlier in _ancestors(name)), None)
                if shadow is not None:
                    self.report(
                        handler,
                        f"`except {name}` never runs, because `except {shadow}` above it already "
                        f"catches {name}. Order handlers from the most specific exception to the "
                        f"most general.",
                    )
                    break
            caught.extend(names)
        self.generic_visit(node)

    @staticmethod
    def _names(node: ast.expr | None) -> list[str]:
        if node is None:
            return ["BaseException"]
        if isinstance(node, ast.Tuple):
            return [element.id for element in node.elts if isinstance(element, ast.Name)]
        return [node.id] if isinstance(node, ast.Name) else []
