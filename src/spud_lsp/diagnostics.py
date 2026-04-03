from lsprotocol import types

from spud.stage_five.stage_five_token_type import StageFiveTokenType as T
from spud.stage_seven.resolve_error import ResolveError, ResolveErrorKind
from spud.stage_six.parse_error import ParseContext, ParseContextKind, ParseError, ParseErrorKind
from spud.stage_six.program import Program

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


_RESOLVE_MESSAGES: dict[ResolveErrorKind, str] = {
    ResolveErrorKind.UNDEFINED_VARIABLE: "undefined variable '{name}'",
    ResolveErrorKind.DUPLICATE_BINDING: "duplicate binding '{name}'",
    ResolveErrorKind.SHADOWED_BINDING: "'{name}' shadows an outer binding",
}


class DiagnosticsHandler:
    def diagnose(self, program: Program) -> list[types.Diagnostic]:
        """Convert parse and resolve errors from a Program into LSP diagnostics."""
        return [self._to_diagnostic(error) for error in program.errors]

    def _to_diagnostic(self, error: ParseError | ResolveError) -> types.Diagnostic:
        match error:
            case ParseError():
                return self._parse_error_diagnostic(error)
            case ResolveError():
                return self._resolve_error_diagnostic(error)

    def _parse_error_diagnostic(self, error: ParseError) -> types.Diagnostic:
        message: str
        match error.kind:
            case ParseErrorKind.UNEXPECTED_END:
                message = "unexpected end of input"
                if error.expected:
                    message += f", expected {_token_label(error.expected)}"
            case ParseErrorKind.UNEXPECTED_TOKEN:
                got_label: str = _token_label(error.got) if error.got else "token"
                message = f"unexpected {got_label}"
                if error.expected:
                    message += f", expected {_token_label(error.expected)}"

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
        template = _RESOLVE_MESSAGES.get(error.kind, error.kind.value)
        message = template.format(name=error.name)
        return types.Diagnostic(
            range=types.Range(
                start=types.Position(line=error.position.line, character=error.position.column),
                end=types.Position(line=error.position.line, character=error.position.column + len(error.name)),
            ),
            severity=types.DiagnosticSeverity.Error,
            source="spud",
            message=message,
        )
