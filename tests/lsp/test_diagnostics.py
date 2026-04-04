from lsprotocol import types

from spud.core.position import Position
from spud.core.resolve_errors.duplicate_binding_error import DuplicateBindingError
from spud.core.resolve_errors.shadowed_binding_error import ShadowedBindingError
from spud.core.resolve_errors.undefined_variable_error import UndefinedVariableError
from spud.stage_five.stage_five_token_type import StageFiveTokenType as T
from spud.stage_six.parse_errors.unexpected_token_error import UnexpectedTokenError
from spud.stage_six.program import Program
from spud_lsp.diagnostics import DiagnosticsHandler

P = Position(line=0, column=0)


def _program(errors=None):
    return Program(position=P, end=P, body=[], errors=errors or [])


class TestResolveErrorDiagnostics:
    def test_undefined_variable(self):
        program = _program(
            [
                UndefinedVariableError(position=Position(line=2, column=5), name="w"),
            ]
        )
        diags = DiagnosticsHandler().diagnose(program)
        assert len(diags) == 1
        assert diags[0].message == "undefined variable 'w'"
        assert diags[0].range.start.line == 2
        assert diags[0].range.start.character == 5
        assert diags[0].severity == types.DiagnosticSeverity.Error
        assert diags[0].source == "spud"

    def test_duplicate_binding(self):
        program = _program(
            [
                DuplicateBindingError(position=Position(line=1, column=0), name="x"),
            ]
        )
        diags = DiagnosticsHandler().diagnose(program)
        assert len(diags) == 1
        assert diags[0].message == "duplicate binding 'x'"

    def test_shadowed_binding(self):
        program = _program(
            [
                ShadowedBindingError(position=Position(line=3, column=6), name="val"),
            ]
        )
        diags = DiagnosticsHandler().diagnose(program)
        assert len(diags) == 1
        assert diags[0].message == "'val' shadows an outer binding"

    def test_resolve_error_range_spans_name(self):
        program = _program(
            [
                UndefinedVariableError(position=Position(line=0, column=3), name="foo"),
            ]
        )
        diags = DiagnosticsHandler().diagnose(program)
        assert diags[0].range.start.character == 3
        assert diags[0].range.end.character == 6


class TestMixedErrors:
    def test_parse_and_resolve_errors(self):
        program = _program(
            [
                UnexpectedTokenError(position=Position(line=0, column=0), got=T.WALRUS),
                UndefinedVariableError(position=Position(line=1, column=5), name="y"),
            ]
        )
        diags = DiagnosticsHandler().diagnose(program)
        assert len(diags) == 2
        assert "unexpected" in diags[0].message
        assert "undefined variable 'y'" == diags[1].message


class TestNoErrors:
    def test_empty_errors(self):
        program = _program()
        diags = DiagnosticsHandler().diagnose(program)
        assert diags == []
