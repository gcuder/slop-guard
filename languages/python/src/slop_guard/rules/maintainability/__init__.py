"""Rules for code that is hard to change later: the book's maintainability chapter."""

from __future__ import annotations

from ...rule import Rule
from .no_computed_attribute_names import NoComputedAttributeNames
from .no_global_statement import NoGlobalStatement
from .no_mixed_return_types import NoMixedReturnTypes
from .no_single_letter_names import NoSingleLetterNames
from .no_wildcard_imports import NoWildcardImports
from .require_with_for_open import RequireWithForOpen

RULES: tuple[type[Rule], ...] = (
    NoComputedAttributeNames,
    NoGlobalStatement,
    NoMixedReturnTypes,
    NoSingleLetterNames,
    NoWildcardImports,
    RequireWithForOpen,
)
