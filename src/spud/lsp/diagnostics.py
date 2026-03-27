from lsprotocol import types

from spud.lsp.lsp_types import ParseResult
from spud.stage_six.parse_error import ParseError, ParseErrorKind


class DiagnosticsHandler:
    def diagnose(self, result: ParseResult) -> list[types.Diagnostic]:
        """Convert a parse result into LSP diagnostics."""
        if not isinstance(result, ParseError):
            return []

        message: str
        match result.kind:
            case ParseErrorKind.UNEXPECTED_END:
                message = "unexpected end of input"
            case ParseErrorKind.UNEXPECTED_TOKEN:
                message = f"unexpected {result.got.value}" if result.got else "unexpected token"

        if result.expected:
            message += f", expected {result.expected.value}"

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
