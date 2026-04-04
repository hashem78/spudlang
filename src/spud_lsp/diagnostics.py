from lsprotocol import types

from spud.stage_five.stage_five_token_type import StageFiveTokenType as T
from spud.stage_seven.resolve_error import (
    DuplicateBindingError,
    ResolveError,
    ShadowedBindingError,
    UndefinedVariableError,
)
from spud.stage_six.parse_errors.parse_context import ParseContext
from spud.stage_six.parse_errors.parse_context_kind import ParseContextKind
from spud.stage_six.parse_errors.parse_error import ParseError
from spud.stage_six.parse_errors.unexpected_end_error import UnexpectedEndError
from spud.stage_six.parse_errors.unexpected_token_error import UnexpectedTokenError
from spud.stage_six.program import Program
from spud_check.type_errors.argument_count_mismatch_error import ArgumentCountMismatchError
from spud_check.type_errors.argument_type_mismatch_error import ArgumentTypeMismatchError
from spud_check.type_errors.branch_type_mismatch_error import BranchTypeMismatchError
from spud_check.type_errors.condition_not_bool_error import ConditionNotBoolError
from spud_check.type_errors.element_type_mismatch_error import ElementTypeMismatchError
from spud_check.type_errors.heterogeneous_list_error import HeterogeneousListError
from spud_check.type_errors.not_callable_error import NotCallableError
from spud_check.type_errors.not_iterable_error import NotIterableError
from spud_check.type_errors.operator_type_error import OperatorTypeError
from spud_check.type_errors.return_type_mismatch_error import ReturnTypeMismatchError
from spud_check.type_errors.type_error import TypeError
from spud_check.type_errors.type_mismatch_error import TypeMismatchError
from spud_check.type_errors.unary_operator_type_error import UnaryOperatorTypeError
from spud_check.type_errors.unknown_type_error import UnknownTypeError

_TOKEN_LABELS: dict[T, str] = {
    T.IDENTIFIER: "identifier",
    T.NEW_LINE: "newline",
    T.STRING: "string",
    T.RAW_STRING: "raw string",
    T.TRUE: "'true'",
    T.FALSE: "'false'",
    T.IF: "'if'",
    T.FOR: "'for'",
    T.WHILE: "'while'",
    T.ELSE: "'else'",
    T.ELIF: "'elif'",
    T.OR: "'or'",
    T.AND: "'and'",
    T.IN: "'in'",
    T.MATCH: "'match'",
    T.WALRUS: "':='",
    T.FAT_ARROW: "'=>'",
    T.PAREN_LEFT: "'('",
    T.PAREN_RIGHT: "')'",
    T.BRACKET_LEFT: "'['",
    T.BRACKET_RIGHT: "']'",
    T.BRACE_LEFT: "'{'",
    T.BRACE_RIGHT: "'}'",
    T.COMMA: "','",
    T.PLUS: "'+'",
    T.MINUS: "'-'",
    T.MULTIPLY: "'*'",
    T.DIVIDE: "'/'",
    T.MODULO: "'%'",
    T.EQUALS: "'=='",
    T.NOT_EQUALS: "'!='",
    T.LESS_THAN: "'<'",
    T.GREATER_THAN: "'>'",
    T.ASSIGN: "'='",
    T.INDENT: "indented block",
    T.DEDENT: "end of block",
}

_CONTEXT_LABELS: dict[ParseContextKind, str] = {
    ParseContextKind.BINDING_TARGET: "in binding target",
    ParseContextKind.BINDING_VALUE: "in binding value",
    ParseContextKind.FUNCTION_PARAMS: "in function parameter list",
    ParseContextKind.FUNCTION_BODY: "in function body",
    ParseContextKind.FUNCTION_ARGS: "in function arguments",
    ParseContextKind.IF_CONDITION: "in if condition",
    ParseContextKind.ELIF_CONDITION: "in elif condition",
    ParseContextKind.IF_BODY: "in if body",
    ParseContextKind.ELIF_BODY: "in elif body",
    ParseContextKind.ELSE_BODY: "in else body",
    ParseContextKind.FOR_VARIABLE: "in for loop variable",
    ParseContextKind.FOR_ITERABLE: "in for loop iterable",
    ParseContextKind.FOR_BODY: "in for loop body",
    ParseContextKind.BLOCK: "in indented block",
    ParseContextKind.EXPRESSION: "in expression",
    ParseContextKind.ORPHANED_ELSE: "'else' without matching 'if'",
    ParseContextKind.ORPHANED_ELIF: "'elif' without matching 'if'",
    ParseContextKind.UNTERMINATED_STRING: "unterminated string literal",
    ParseContextKind.UNTERMINATED_RAW_STRING: "unterminated raw string literal",
}


def _token_label(token_type: T) -> str:
    return _TOKEN_LABELS.get(token_type, token_type.name.lower())


def _context_label(context: ParseContext) -> str:
    if context.kind == ParseContextKind.UNTERMINATED_DELIMITER and context.delimiter:
        return f"unterminated {_token_label(context.delimiter)}"
    return _CONTEXT_LABELS.get(context.kind, context.kind.value)


class DiagnosticsHandler:
    def diagnose(self, program: Program, type_errors: list[TypeError] | None = None) -> list[types.Diagnostic]:
        """Convert parse, resolve, and type errors into LSP diagnostics."""
        diagnostics = [self._to_diagnostic(error) for error in program.errors]
        if type_errors:
            diagnostics.extend(self._type_error_diagnostic(e) for e in type_errors)
        return diagnostics

    def _to_diagnostic(self, error: ParseError | ResolveError) -> types.Diagnostic:
        match error:
            case ParseError():
                return self._parse_error_diagnostic(error)
            case ResolveError():
                return self._resolve_error_diagnostic(error)

    def _parse_error_diagnostic(self, error: ParseError) -> types.Diagnostic:
        message: str
        match error:
            case UnexpectedEndError(expected=expected):
                message = "unexpected end of input"
                if expected:
                    message += f", expected {_token_label(expected)}"
            case UnexpectedTokenError(expected=expected, got=got):
                got_label: str = _token_label(got) if got else "token"
                message = f"unexpected {got_label}"
                if expected:
                    message += f", expected {_token_label(expected)}"

        if error.context:
            message += f" ({_context_label(error.context)})"

        return types.Diagnostic(
            range=types.Range(
                start=types.Position(line=error.position.line, character=error.position.column),
                end=types.Position(line=error.position.line, character=error.position.column + 1),
            ),
            severity=types.DiagnosticSeverity.Error,
            source="spud",
            message=message,
        )

    def _resolve_error_diagnostic(self, error: ResolveError) -> types.Diagnostic:
        message: str
        match error:
            case UndefinedVariableError(name=name):
                message = f"undefined variable '{name}'"
            case DuplicateBindingError(name=name):
                message = f"duplicate binding '{name}'"
            case ShadowedBindingError(name=name):
                message = f"'{name}' shadows an outer binding"
        return types.Diagnostic(
            range=types.Range(
                start=types.Position(line=error.position.line, character=error.position.column),
                end=types.Position(line=error.position.line, character=error.position.column + len(name)),
            ),
            severity=types.DiagnosticSeverity.Error,
            source="spud",
            message=message,
        )

    def _type_error_diagnostic(self, error: TypeError) -> types.Diagnostic:
        message = _format_type_error(error)
        return types.Diagnostic(
            range=types.Range(
                start=types.Position(line=error.position.line, character=error.position.column),
                end=types.Position(line=error.position.line, character=error.position.column + 1),
            ),
            severity=types.DiagnosticSeverity.Error,
            source="spud",
            message=message,
        )


def _format_type_error(error: TypeError) -> str:
    match error:
        case TypeMismatchError(name=name, expected=expected, actual=actual):
            return f"'{name}' declared as {expected.value} but value has type {actual.value}"
        case ArgumentTypeMismatchError(name=name, index=index, expected=expected, actual=actual):
            return f"argument {index} of '{name}' expected {expected.value} but got {actual.value}"
        case ArgumentCountMismatchError(name=name, expected_count=expected, actual_count=actual):
            return f"'{name}' expects {expected} arguments but got {actual}"
        case NotCallableError(name=name):
            return f"'{name}' is not callable"
        case OperatorTypeError(operator=op, left=left, right=right):
            return f"operator '{op}' not supported for {left.value} and {right.value}"
        case UnaryOperatorTypeError(operator=op, operand=operand):
            return f"unary '{op}' not supported for {operand.value}"
        case BranchTypeMismatchError(index=index, expected=expected, actual=actual):
            return f"branch {index} has type {actual.value} but expected {expected.value}"
        case ConditionNotBoolError(actual=actual):
            return f"condition must be Bool but got {actual.value}"
        case NotIterableError(actual=actual):
            return f"for-loop requires List but got {actual.value}"
        case ElementTypeMismatchError(name=name, expected=expected, actual=actual):
            return f"loop variable '{name}' declared as {expected.value} but list element type is {actual.value}"
        case UnknownTypeError(name=name):
            return f"unknown type '{name}'"
        case HeterogeneousListError(index=index, expected=expected, actual=actual):
            return f"list element {index} has type {actual.value} but expected {expected.value}"
        case ReturnTypeMismatchError(expected=expected, actual=actual):
            return f"function returns {actual.value} but declared return type is {expected.value}"
        case _:
            return error.kind.value
