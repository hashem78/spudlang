from enum import Enum


class StageSixTokenType(str, Enum):
    STRING_LITERAL = "string_literal"
    RAW_STRING_LITERAL = "raw_string_literal"
    NUMERIC_LITERAL = "numeric_literal"
    BOOLEAN_LITERAL = "boolean_literal"
    ASSIGNMENT = "assignment"
    FUNCTION_DEF = "function_def"
    FUNCTION_CALL = "function_call"
    BINARY_OP = "binary_op"
    FOR_LOOP = "for_loop"
    WHILE_LOOP = "while_loop"
    IF_EXPR = "if_expr"
    ELIF_EXPR = "elif_expr"
    ELSE_EXPR = "else_expr"
    MATCH_EXPR = "match_expr"
    EXPRESSION = "expression"
