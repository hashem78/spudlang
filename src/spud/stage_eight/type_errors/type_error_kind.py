from enum import Enum


class TypeErrorKind(str, Enum):
    TYPE_MISMATCH = "type_mismatch"
    ARGUMENT_TYPE_MISMATCH = "argument_type_mismatch"
    ARGUMENT_COUNT_MISMATCH = "argument_count_mismatch"
    NOT_CALLABLE = "not_callable"
    OPERATOR_TYPE_ERROR = "operator_type_error"
    UNARY_OPERATOR_TYPE_ERROR = "unary_operator_type_error"
    BRANCH_TYPE_MISMATCH = "branch_type_mismatch"
    CONDITION_NOT_BOOL = "condition_not_bool"
    NOT_ITERABLE = "not_iterable"
    ELEMENT_TYPE_MISMATCH = "element_type_mismatch"
    UNKNOWN_TYPE = "unknown_type"
    HETEROGENEOUS_LIST = "heterogeneous_list"
    RETURN_TYPE_MISMATCH = "return_type_mismatch"
