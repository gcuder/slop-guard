"""Rules for code that reads worse than it needs to: the book's readability chapter."""

from __future__ import annotations

from ...rule import Rule
from .no_camel_case_functions import NoCamelCaseFunctions
from .no_comparison_to_bool import NoComparisonToBool
from .no_comparison_to_none import NoComparisonToNone
from .no_identity_comparison_to_literal import NoIdentityComparisonToLiteral
from .no_type_comparison import NoTypeComparison
from .no_type_in_name import NoTypeInName
from .prefer_comprehension_over_map_filter import PreferComprehensionOverMapFilter
from .prefer_dict_comprehension import PreferDictComprehension
from .prefer_dict_items import PreferDictItems
from .prefer_eafp_for_files import PreferEafpForFiles
from .prefer_enumerate import PreferEnumerate
from .prefer_format_mapping import PreferFormatMapping
from .prefer_named_tuple import PreferNamedTuple
from .prefer_tuple_swap import PreferTupleSwap
from .prefer_zip import PreferZip

RULES: tuple[type[Rule], ...] = (
    NoCamelCaseFunctions,
    NoComparisonToBool,
    NoComparisonToNone,
    NoIdentityComparisonToLiteral,
    NoTypeComparison,
    NoTypeInName,
    PreferComprehensionOverMapFilter,
    PreferDictComprehension,
    PreferDictItems,
    PreferEafpForFiles,
    PreferEnumerate,
    PreferFormatMapping,
    PreferNamedTuple,
    PreferTupleSwap,
    PreferZip,
)
