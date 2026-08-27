"""Require `__exit__` to accept the three arguments the interpreter passes."""

from __future__ import annotations

from ...rule import FunctionNode, Rule


class RequireExitSignature(Rule):
    name = "require-exit-signature"
    group = "correctness"
    reference = "https://docs.quantifiedcode.com/python-anti-patterns/correctness/exit_must_accept_three_arguments.html"
    description = "Require `__exit__` to take `self` plus the exception type, value, and traceback."

    def visit_FunctionDef(self, node: FunctionNode) -> None:
        if node.name == "__exit__":
            positional = [*node.args.posonlyargs, *node.args.args]
            if len(positional) != 4 and node.args.vararg is None:
                self.report(
                    node,
                    f"`__exit__` takes {len(positional)} argument(s), but the interpreter always "
                    f"calls it with the exception type, value, and traceback. Declare "
                    f"`__exit__(self, exception_type, exception, traceback)`.",
                )
        self.generic_visit(node)

    visit_AsyncFunctionDef = visit_FunctionDef
