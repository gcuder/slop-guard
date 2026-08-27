"""Require each cast to state the invariant that makes it sound."""

from __future__ import annotations

import ast

from ...rule import Rule


class RequireSafetyCommentForCast(Rule):
    name = "require-safety-comment-for-cast"
    group = "evidence"
    description = "Require a `# SAFETY:` comment above every `typing.cast` call."

    def visit_Call(self, node: ast.Call) -> None:
        if self.is_cast_call(node) and not self.source.has_safety_comment(node.lineno):
            target = self.unparse(node.args[0]) if node.args else "the target type"
            self.report(
                node,
                f"This cast to `{target}` is unexplained. Add a `# SAFETY:` comment naming the "
                f"check that already guarantees the type, or parse the value instead.",
            )
        self.generic_visit(node)
