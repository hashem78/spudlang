from lsprotocol import types

from spud.core.position import Position
from spud.core.resolve_errors.duplicate_binding_error import DuplicateBindingError
from spud.core.resolve_errors.shadowed_binding_error import ShadowedBindingError
from spud.core.resolve_errors.undefined_variable_error import UndefinedVariableError
from spud.core.types.spud_type_kind import SpudTypeKind
from spud.stage_five.stage_five_token_type import StageFiveTokenType as T
from spud.stage_six.parse_errors.unexpected_token_error import UnexpectedTokenError
from spud.stage_six.program import Program
from spud_check.type_errors.argument_count_mismatch_error import ArgumentCountMismatchError
from spud_check.type_errors.condition_not_bool_error import ConditionNotBoolError
from spud_check.type_errors.not_callable_error import NotCallableError
from spud_check.type_errors.operator_type_error import OperatorTypeError
from spud_check.type_errors.return_type_mismatch_error import ReturnTypeMismatchError
from spud_check.type_errors.type_mismatch_error import TypeMismatchError
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


class TestTypeErrorDiagnostics:
    def test_type_mismatch(self):
        program = _program()
        errors = [
            TypeMismatchError(
                position=Position(line=0, column=0),
                name="x",
                expected=SpudTypeKind.INT,
                actual=SpudTypeKind.FLOAT,
            ),
        ]
        diags = DiagnosticsHandler().diagnose(program, type_errors=errors)
        assert len(diags) == 1
        assert "'x' declared as int but value has type float" == diags[0].message
        assert diags[0].severity == types.DiagnosticSeverity.Error
        assert diags[0].source == "spud"

    def test_operator_type_error(self):
        program = _program()
        errors = [
            OperatorTypeError(
                position=Position(line=1, column=3),
                operator="+",
                left=SpudTypeKind.INT,
                right=SpudTypeKind.STRING,
            ),
        ]
        diags = DiagnosticsHandler().diagnose(program, type_errors=errors)
        assert len(diags) == 1
        assert "operator '+' not supported for int and string" == diags[0].message

    def test_argument_count_mismatch(self):
        program = _program()
        errors = [
            ArgumentCountMismatchError(
                position=Position(line=2, column=0),
                name="foo",
                expected_count=2,
                actual_count=3,
            ),
        ]
        diags = DiagnosticsHandler().diagnose(program, type_errors=errors)
        assert len(diags) == 1
        assert "'foo' expects 2 arguments but got 3" == diags[0].message

    def test_not_callable(self):
        program = _program()
        errors = [
            NotCallableError(
                position=Position(line=0, column=5),
                name="val",
            ),
        ]
        diags = DiagnosticsHandler().diagnose(program, type_errors=errors)
        assert len(diags) == 1
        assert "'val' is not callable" == diags[0].message

    def test_condition_not_bool(self):
        program = _program()
        errors = [
            ConditionNotBoolError(
                position=Position(line=3, column=0),
                actual=SpudTypeKind.INT,
            ),
        ]
        diags = DiagnosticsHandler().diagnose(program, type_errors=errors)
        assert len(diags) == 1
        assert "condition must be Bool but got int" == diags[0].message

    def test_return_type_mismatch(self):
        program = _program()
        errors = [
            ReturnTypeMismatchError(
                position=Position(line=1, column=2),
                expected=SpudTypeKind.INT,
                actual=SpudTypeKind.STRING,
            ),
        ]
        diags = DiagnosticsHandler().diagnose(program, type_errors=errors)
        assert len(diags) == 1
        assert "function returns string but declared return type is int" == diags[0].message
