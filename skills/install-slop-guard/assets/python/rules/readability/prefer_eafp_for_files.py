"""Prefer trying the operation over checking whether a path exists first."""

from __future__ import annotations

import ast

from ...rule import Rule

EXISTENCE_CHECKS = frozenset({"os.path.exists", "os.path.isfile", "os.path.isdir", "pathlib.Path.exists"})
FILE_OPERATIONS = frozenset({"open", "os.unlink", "os.remove", "os.rmdir", "os.rename", "shutil.rmtree"})


class PreferEafpForFiles(Rule):
    name = "prefer-eafp-for-files"
    group = "readability"
    reference = "https://docs.quantifiedcode.com/python-anti-patterns/readability/asking_for_permission_instead_of_forgiveness_when_working_with_files.html"
    description = "Prefer handling `OSError` to checking `os.path.exists` before touching a file."

    def visit_If(self, node: ast.If) -> None:
        check = self._existence_check(node.test)
        if check is not None and self._touches_file(node.body):
            self.report(
                node,
                f"`{check}` can be true and then false a moment later, so this check does not "
                f"make the operation safe. Do the work and handle `OSError`.",
            )
        self.generic_visit(node)

    def _existence_check(self, test: ast.expr) -> str | None:
        candidate = test.operand if isinstance(test, ast.UnaryOp) and isinstance(test.op, ast.Not) else test
        if isinstance(candidate, ast.Call):
            name = self.unparse(candidate.func)
            if name in EXISTENCE_CHECKS or name.endswith(".exists") or name.endswith(".is_file"):
                return f"{name}(...)"
        return None

    def _touches_file(self, body: list[ast.stmt]) -> bool:
        for statement in body:
            for node in ast.walk(statement):
                if isinstance(node, ast.Call) and self.unparse(node.func) in FILE_OPERATIONS:
                    return True
        return False
