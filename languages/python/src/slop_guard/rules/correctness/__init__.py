"""Rules for code that misbehaves at runtime: the book's correctness chapter."""

from __future__ import annotations

from ...rule import Rule
from .no_bad_super_arguments import NoBadSuperArguments
from .no_bare_except import NoBareExcept
from .no_builtin_shadowing import NoBuiltinShadowing
from .no_java_style_accessors import NoJavaStyleAccessors
from .no_lambda_assignment import NoLambdaAssignment
from .no_loop_else_without_break import NoLoopElseWithoutBreak
from .no_method_without_receiver_use import NoMethodWithoutReceiverUse
from .no_mixed_indentation import NoMixedIndentation
from .no_mutable_default_argument import NoMutableDefaultArgument
from .no_protected_member_access import NoProtectedMemberAccess
from .no_return_value_in_init import NoReturnValueInInit
from .no_tab_indentation import NoTabIndentation
from .no_unreachable_except_clause import NoUnreachableExceptClause
from .prefer_defaultdict import PreferDefaultdict
from .prefer_dict_get import PreferDictGet
from .prefer_explicit_unpacking import PreferExplicitUnpacking
from .prefer_loop_else import PreferLoopElse
from .prefer_setdefault import PreferSetdefault
from .require_exit_signature import RequireExitSignature
from .require_method_self import RequireMethodSelf

RULES: tuple[type[Rule], ...] = (
    NoBadSuperArguments,
    NoBareExcept,
    NoBuiltinShadowing,
    NoJavaStyleAccessors,
    NoLambdaAssignment,
    NoLoopElseWithoutBreak,
    NoMethodWithoutReceiverUse,
    NoMixedIndentation,
    NoMutableDefaultArgument,
    NoProtectedMemberAccess,
    NoReturnValueInInit,
    NoTabIndentation,
    NoUnreachableExceptClause,
    PreferDefaultdict,
    PreferDictGet,
    PreferExplicitUnpacking,
    PreferLoopElse,
    PreferSetdefault,
    RequireExitSignature,
    RequireMethodSelf,
)
