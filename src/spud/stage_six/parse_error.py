from enum import Enum

from pydantic import BaseModel

from spud.core.position import Position
from spud.stage_five.stage_five_token_type import StageFiveTokenType


class ParseErrorKind(str, Enum):
    UNEXPECTED_END = "unexpected_end"
    UNEXPECTED_TOKEN = "unexpected_token"


class ParseContextKind(str, Enum):
    BINDING_TARGET = "binding_target"
    BINDING_VALUE = "binding_value"
    FUNCTION_PARAMS = "function_params"
    FUNCTION_BODY = "function_body"
    FUNCTION_ARGS = "function_args"
    IF_CONDITION = "if_condition"
    ELIF_CONDITION = "elif_condition"
    IF_BODY = "if_body"
    ELIF_BODY = "elif_body"
    ELSE_BODY = "else_body"
    FOR_VARIABLE = "for_variable"
    FOR_ITERABLE = "for_iterable"
    FOR_BODY = "for_body"
    BLOCK = "block"
    EXPRESSION = "expression"


class ParseContext(BaseModel, frozen=True):
    kind: ParseContextKind


class ParseError(BaseModel, frozen=True):
    kind: ParseErrorKind
    position: Position
    expected: StageFiveTokenType | None = None
    got: StageFiveTokenType | None = None
    context: ParseContext | None = None


def with_context(error: ParseError, context: ParseContext) -> ParseError:
    """Attach context to an error if it doesn't already have one."""
    if error.context is None:
        return error.model_copy(update={"context": context})
    return error


def ctx(kind: ParseContextKind) -> ParseContext:
    """Shorthand for creating a ParseContext."""
    return ParseContext(kind=kind)
