import pytest

from spud.core.pipeline import ParsedProgram, Pipeline, ResolvedProgram
from spud.core.resolve_errors.resolve_error_kind import ResolveErrorKind
from spud.core.string_reader import StringReader
from spud.di.container import Container
from spud.stage_five.stage_five import StageFive
from spud.stage_four.stage_four import StageFour
from spud.stage_one.stage_one import StageOne
from spud.stage_six.binding import Binding
from spud.stage_six.int_literal import IntLiteral
from spud.stage_three.stage_three import StageThree
from spud.stage_two.stage_two import StageTwo


def _pipeline() -> Pipeline:
    return Container().pipeline()


def _reader(text: str) -> StringReader:
    return StringReader(text)


class TestPipelineGetReturnTypes:
    def test_get_stage_one_returns_stage_one_instance(self):
        pipeline = _pipeline()
        result = pipeline.get(StageOne, _reader("x : Int := 1"))
        assert isinstance(result, StageOne)

    def test_get_stage_two_returns_stage_two_instance(self):
        pipeline = _pipeline()
        result = pipeline.get(StageTwo, _reader("x : Int := 1"))
        assert isinstance(result, StageTwo)

    def test_get_stage_three_returns_stage_three_instance(self):
        pipeline = _pipeline()
        result = pipeline.get(StageThree, _reader("x : Int := 1"))
        assert isinstance(result, StageThree)

    def test_get_stage_four_returns_stage_four_instance(self):
        pipeline = _pipeline()
        result = pipeline.get(StageFour, _reader("x : Int := 1"))
        assert isinstance(result, StageFour)

    def test_get_stage_five_returns_stage_five_instance(self):
        pipeline = _pipeline()
        result = pipeline.get(StageFive, _reader("x : Int := 1"))
        assert isinstance(result, StageFive)

    def test_get_parsed_program_returns_parsed_program_instance(self):
        pipeline = _pipeline()
        result = pipeline.get(ParsedProgram, _reader("x : Int := 1"))
        assert isinstance(result, ParsedProgram)

    def test_get_parsed_program_has_tokens(self):
        pipeline = _pipeline()
        result = pipeline.get(ParsedProgram, _reader("x : Int := 1"))
        assert hasattr(result, "tokens")
        assert hasattr(result, "program")

    def test_get_resolved_program_returns_resolved_program_instance(self):
        pipeline = _pipeline()
        result = pipeline.get(ResolvedProgram, _reader("x : Int := 1"))
        assert isinstance(result, ResolvedProgram)

    def test_get_resolved_program_has_all_fields(self):
        pipeline = _pipeline()
        result = pipeline.get(ResolvedProgram, _reader("x : Int := 1"))
        assert hasattr(result, "tokens")
        assert hasattr(result, "program")
        assert hasattr(result, "resolve_result")


class TestPipelineRun:
    def test_run_returns_resolved_program(self):
        pipeline = _pipeline()
        result = pipeline.run(_reader("x : Int := 1"))
        assert isinstance(result, ResolvedProgram)

    def test_run_valid_program_has_no_errors(self):
        pipeline = _pipeline()
        result = pipeline.run(_reader("x : Int := 1"))
        assert result.resolve_result.errors == []

    def test_run_empty_program_has_no_errors(self):
        pipeline = _pipeline()
        result = pipeline.run(_reader(""))
        assert result.resolve_result.errors == []

    def test_run_undefined_variable_produces_error(self):
        pipeline = _pipeline()
        result = pipeline.run(_reader("x : Int := y"))
        assert len(result.resolve_result.errors) > 0

    def test_run_undefined_variable_error_kind(self):
        pipeline = _pipeline()
        result = pipeline.run(_reader("x : Int := y"))
        error = result.resolve_result.errors[0]
        assert error.kind == ResolveErrorKind.UNDEFINED_VARIABLE

    def test_run_undefined_variable_error_name(self):
        pipeline = _pipeline()
        result = pipeline.run(_reader("x : Int := y"))
        error = result.resolve_result.errors[0]
        assert error.name == "y"

    def test_run_duplicate_binding_produces_error(self):
        pipeline = _pipeline()
        result = pipeline.run(_reader("x : Int := 1\nx : Int := 2"))
        assert len(result.resolve_result.errors) > 0
        kinds = [e.kind for e in result.resolve_result.errors]
        assert ResolveErrorKind.DUPLICATE_BINDING in kinds


class TestParsedProgramContents:
    def test_tokens_non_empty_for_non_empty_input(self):
        pipeline = _pipeline()
        result = pipeline.get(ParsedProgram, _reader("x : Int := 1"))
        assert len(result.tokens) > 0

    def test_tokens_empty_for_empty_input(self):
        pipeline = _pipeline()
        result = pipeline.get(ParsedProgram, _reader(""))
        assert result.tokens == []

    def test_program_body_has_correct_statement_count(self):
        pipeline = _pipeline()
        result = pipeline.get(ParsedProgram, _reader("x : Int := 1\ny : Int := 2"))
        assert len(result.program.body) == 2

    def test_program_body_single_statement(self):
        pipeline = _pipeline()
        result = pipeline.get(ParsedProgram, _reader("x : Int := 1"))
        assert len(result.program.body) == 1

    def test_program_body_empty_for_empty_input(self):
        pipeline = _pipeline()
        result = pipeline.get(ParsedProgram, _reader(""))
        assert result.program.body == []

    def test_program_body_contains_binding_node(self):
        pipeline = _pipeline()
        result = pipeline.get(ParsedProgram, _reader("x : Int := 42"))
        assert len(result.program.body) == 1
        assert isinstance(result.program.body[0], Binding)

    def test_program_binding_value_is_int_literal(self):
        pipeline = _pipeline()
        result = pipeline.get(ParsedProgram, _reader("x : Int := 42"))
        node = result.program.body[0]
        assert isinstance(node, Binding)
        assert isinstance(node.value, IntLiteral)
        assert node.value.value == 42


class TestResolvedProgramContents:
    def test_environment_has_top_level_binding(self):
        pipeline = _pipeline()
        result = pipeline.run(_reader("x : Int := 5"))
        assert result.resolve_result.environment.contains("x")

    def test_environment_has_multiple_bindings(self):
        pipeline = _pipeline()
        result = pipeline.run(_reader("x : Int := 1\ny : Int := 2"))
        env = result.resolve_result.environment
        assert env.contains("x")
        assert env.contains("y")

    def test_environment_does_not_contain_undefined_name(self):
        pipeline = _pipeline()
        result = pipeline.run(_reader("x : Int := 1"))
        env = result.resolve_result.environment
        assert not env.contains("z")

    def test_resolve_result_errors_empty_for_valid_program(self):
        pipeline = _pipeline()
        result = pipeline.run(_reader("x : Int := 1\ny : Int := x + 1"))
        assert result.resolve_result.errors == []

    def test_resolve_result_errors_non_empty_for_undefined_variable(self):
        pipeline = _pipeline()
        result = pipeline.run(_reader("result : Int := missing"))
        assert len(result.resolve_result.errors) > 0

    def test_resolve_result_shadowed_binding_produces_error(self):
        pipeline = _pipeline()
        result = pipeline.run(_reader("x : Int := 5\nf : Function[[Int], Int] := (x : Int) : Int =>\n  x + 1"))
        kinds = [e.kind for e in result.resolve_result.errors]
        assert ResolveErrorKind.SHADOWED_BINDING in kinds


class TestStepChainIndependence:
    def test_two_runs_produce_independent_results(self):
        pipeline = _pipeline()
        result1 = pipeline.run(_reader("x : Int := 1"))
        result2 = pipeline.run(_reader("y : Int := 2"))
        env1 = result1.resolve_result.environment
        env2 = result2.resolve_result.environment
        assert env1.contains("x")
        assert not env1.contains("y")
        assert env2.contains("y")
        assert not env2.contains("x")

    def test_two_runs_produce_independent_token_lists(self):
        pipeline = _pipeline()
        result1 = pipeline.run(_reader("x : Int := 1"))
        result2 = pipeline.run(_reader("longer_name : Int := 9999"))
        assert result1.tokens is not result2.tokens

    def test_two_parsed_programs_have_independent_bodies(self):
        pipeline = _pipeline()
        result1 = pipeline.get(ParsedProgram, _reader("x : Int := 1"))
        result2 = pipeline.get(ParsedProgram, _reader("a : Int := 2\nb : Int := 3"))
        assert len(result1.program.body) == 1
        assert len(result2.program.body) == 2

    def test_pipeline_reuse_across_different_inputs(self):
        pipeline = _pipeline()
        for i in range(3):
            result = pipeline.run(_reader(f"var{i} : Int := {i}"))
            assert result.resolve_result.errors == []
            assert result.resolve_result.environment.contains(f"var{i}")


class TestUnknownStageType:
    def test_get_unregistered_type_raises_key_error(self):
        pipeline = _pipeline()

        class UnregisteredStage:
            pass

        with pytest.raises(KeyError):
            pipeline.get(UnregisteredStage, _reader("x : Int := 1"))  # type: ignore[arg-type]
