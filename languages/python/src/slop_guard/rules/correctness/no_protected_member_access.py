"""Reject reads of another object's protected members."""

from __future__ import annotations

import ast

from ...rule import Rule


class NoProtectedMemberAccess(Rule):
    name = "no-protected-member-access"
    group = "correctness"
    reference = "https://docs.quantifiedcode.com/python-anti-patterns/correctness/accessing_a_protected_member_from_outside_the_class.html"
    description = "Disallow reading `owner._member` from outside the owning class."

    def visit_Attribute(self, node: ast.Attribute) -> None:
        owner = node.value
        if (
            node.attr.startswith("_")
            and not node.attr.startswith("__")
            and isinstance(owner, ast.Name)
            and owner.id not in {"self", "cls", "mcs"}
        ):
            self.report(
                node,
                f"`{owner.id}.{node.attr}` reaches past the public interface of another object. "
                f"The leading underscore says the owner may change it without warning; ask the "
                f"owner for a public accessor instead.",
            )
        self.generic_visit(node)
