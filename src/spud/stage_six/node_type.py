from enum import Enum


class NodeType(str, Enum):
    IDENTIFIER = "identifier"
    NUMERIC_LITERAL = "numeric_literal"
    STRING_LITERAL = "string_literal"
    RAW_STRING_LITERAL = "raw_string_literal"
    BOOLEAN_LITERAL = "boolean_literal"
    BINDING = "binding"
    FUNCTION_DEF = "function_def"
    FUNCTION_CALL = "function_call"
    BINARY_OP = "binary_op"
    UNARY_OP = "unary_op"
    CONDITION_BRANCH = "condition_branch"
    IF_ELSE = "if_else"
    FOR_LOOP = "for_loop"
    INLINE_FUNCTION_DEF = "inline_function_def"
    UNIT_LITERAL = "unit_literal"
    PROGRAM = "program"
