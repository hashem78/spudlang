from lsprotocol import types

from spud.lsp.lsp_types import ParseResult
from spud.stage_five.stage_five_token_type import StageFiveTokenType as T
from spud.stage_six.parse_error import ParseError, ParseErrorKind

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


def _token_label(token_type: T) -> str:
    return _TOKEN_LABELS.get(token_type, token_type.name.lower())


class DiagnosticsHandler:
    def diagnose(self, result: ParseResult) -> list[types.Diagnostic]:
        """Convert a parse result into LSP diagnostics."""
        if not isinstance(result, ParseError):
            return []

        message: str
        match result.kind:
            case ParseErrorKind.UNEXPECTED_END:
                message = "unexpected end of input"
                if result.expected:
                    message += f", expected {_token_label(result.expected)}"
            case ParseErrorKind.UNEXPECTED_TOKEN:
                got_label: str = _token_label(result.got) if result.got else "token"
                message = f"unexpected {got_label}"
                if result.expected:
                    message += f", expected {_token_label(result.expected)}"

        return [
            types.Diagnostic(
                range=types.Range(
                    start=types.Position(line=result.position.line, character=result.position.column),
                    end=types.Position(line=result.position.line, character=result.position.column + 1),
                ),
                severity=types.DiagnosticSeverity.Error,
                source="spud",
                message=message,
            )
        ]
