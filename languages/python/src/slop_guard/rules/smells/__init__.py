"""Rules for the code smells catalogued at refactoring.guru."""

from __future__ import annotations

from ...rule import Rule
from .no_commented_out_code import NoCommentedOutCode
from .no_data_clumps import NoDataClumps
from .no_data_class import NoDataClass
from .no_duplicate_code import NoDuplicateCode
from .no_feature_envy import NoFeatureEnvy
from .no_large_class import NoLargeClass
from .no_lazy_class import NoLazyClass
from .no_long_method import NoLongMethod
from .no_long_parameter_list import NoLongParameterList
from .no_message_chains import NoMessageChains
from .no_middle_man import NoMiddleMan
from .no_primitive_obsession import NoPrimitiveObsession
from .no_refused_bequest import NoRefusedBequest
from .no_temporary_field import NoTemporaryField
from .no_type_code_switch import NoTypeCodeSwitch
from .no_unreachable_code import NoUnreachableCode
from .no_unused_parameter import NoUnusedParameter

RULES: tuple[type[Rule], ...] = (
    NoCommentedOutCode,
    NoDataClass,
    NoDataClumps,
    NoDuplicateCode,
    NoFeatureEnvy,
    NoLargeClass,
    NoLazyClass,
    NoLongMethod,
    NoLongParameterList,
    NoMessageChains,
    NoMiddleMan,
    NoPrimitiveObsession,
    NoRefusedBequest,
    NoTemporaryField,
    NoTypeCodeSwitch,
    NoUnreachableCode,
    NoUnusedParameter,
)
