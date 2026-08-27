"""Rules that reject code claiming more than the program can prove."""

from __future__ import annotations

from ...rule import Rule
from .no_any_parameters import NoAnyParameters
from .no_any_returns import NoAnyReturns
from .no_any_type_aliases import NoAnyTypeAliases
from .no_chained_casts import NoChainedCasts
from .no_conditional_empty_dict_spread import NoConditionalEmptyDictSpread
from .no_dynamic_attribute_access import NoDynamicAttributeAccess
from .no_forbidden_terms_in_symbol_names import NoForbiddenTermsInSymbolNames
from .no_known_value_widening import NoKnownValueWidening
from .no_module_mocking import NoModuleMocking
from .no_object_parameters import NoObjectParameters
from .no_runtime_isinstance import NoRuntimeIsinstance
from .no_silent_exception_swallow import NoSilentExceptionSwallow
from .no_unsafe_dictionary_type import NoUnsafeDictionaryType
from .no_widen_then_cast import NoWidenThenCast
from .require_safety_comment_for_cast import RequireSafetyCommentForCast

RULES: tuple[type[Rule], ...] = (
    NoAnyParameters,
    NoAnyReturns,
    NoAnyTypeAliases,
    NoChainedCasts,
    NoConditionalEmptyDictSpread,
    NoDynamicAttributeAccess,
    NoForbiddenTermsInSymbolNames,
    NoKnownValueWidening,
    NoModuleMocking,
    NoObjectParameters,
    NoRuntimeIsinstance,
    NoSilentExceptionSwallow,
    NoUnsafeDictionaryType,
    NoWidenThenCast,
    RequireSafetyCommentForCast,
)
