"""Reject module-level patching in favour of real dependency seams."""

from __future__ import annotations

import ast

from ...rule import Rule

PATCH_PATHS = (
    "unittest.mock.patch",
    "mock.patch",
    "pytest_mock.patch",
)


class NoModuleMocking(Rule):
    name = "no-module-mocking"
    group = "evidence"
    description = (
        "Disallow `mock.patch`, `mocker.patch`, and `monkeypatch.setattr` module patching; inject "
        "the dependency instead."
    )

    def visit_Call(self, node: ast.Call) -> None:
        target = self._patch_target(node.func)
        if target is not None:
            self.report(
                node,
                f"`{target}` replaces a module attribute at runtime, so the test proves nothing "
                f"about how the real code is wired. Pass the dependency in and substitute a fake "
                f"at the call site.",
            )
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        for decorator in node.decorator_list:
            call = decorator.func if isinstance(decorator, ast.Call) else decorator
            target = self._patch_target(call)
            if target is not None:
                self.report(
                    decorator,
                    f"`{target}` patches a module for this test, so the test proves nothing about "
                    f"how the real code is wired. Inject the dependency instead.",
                )
        self.generic_visit(node)

    visit_AsyncFunctionDef = visit_FunctionDef

    def _patch_target(self, function: ast.expr) -> str | None:
        text = self.unparse(function)
        if self.imports.matches(function, *PATCH_PATHS):
            return text
        if isinstance(function, ast.Attribute):
            owner = function.value
            root = self.unparse(owner)
            if function.attr in {"patch", "object"} and root.split(".")[0] in {"mock", "mocker", "unittest"}:
                return text
            if function.attr in {"setattr", "setitem", "delattr"} and root.split(".")[0] == "monkeypatch":
                return text
        if isinstance(function, ast.Name) and function.id == "patch":
            return text
        return None
