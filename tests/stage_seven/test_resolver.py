import structlog

from spud.stage_seven.resolve_error import ResolveErrorKind
from spud.stage_seven.resolve_result import ResolveResult
from spud.stage_seven.stage_seven import StageSeven
from spud.stage_six.program import Program
from tests.stage_six.helpers import parse


def _resolve(text: str) -> ResolveResult:
    program = parse(text)
    assert isinstance(program, Program)
    resolver = StageSeven(logger=structlog.get_logger())
    return resolver.resolve(program)


class TestValidPrograms:
    def test_empty_program(self):
        result = _resolve("")
        assert result.errors == []

    def test_simple_binding(self):
        result = _resolve("x := 5")
        assert result.errors == []

    def test_multiple_bindings_sequential(self):
        result = _resolve("x := 1\ny := 2")
        assert result.errors == []

    def test_binding_referenced_after_definition(self):
        result = _resolve("x := 5\ny := x")
        assert result.errors == []

    def test_function_binding_with_param(self):
        result = _resolve("f := (x) =>\n  x")
        assert result.errors == []

    def test_function_body_uses_param(self):
        result = _resolve("f := (x) =>\n  x + 1")
        assert result.errors == []

    def test_function_body_uses_outer_binding(self):
        result = _resolve("n := 10\nf := (x) =>\n  x + n")
        assert result.errors == []

    def test_inline_function_binding(self):
        result = _resolve("add := (a, b) => a + b")
        assert result.errors == []

    def test_function_call_to_known_binding(self):
        result = _resolve("f := (x) =>\n  x\nf(1)")
        assert result.errors == []

    def test_list_literal_with_known_identifiers(self):
        result = _resolve("x := 1\ny := 2\nz := [x, y]")
        assert result.errors == []

    def test_for_loop_over_known_binding(self):
        result = _resolve("items := [1, 2]\nfor x in items\n  x")
        assert result.errors == []

    def test_if_else_with_known_condition(self):
        result = _resolve("flag := true\nif flag\n  1\nelse\n  2")
        assert result.errors == []

    def test_binding_used_in_binary_op(self):
        result = _resolve("a := 3\nb := a + 1")
        assert result.errors == []

    def test_binding_used_in_unary_op(self):
        result = _resolve("a := 5\nb := -a")
        assert result.errors == []


class TestSelfRecursion:
    def test_function_can_call_itself(self):
        result = _resolve("f := (x) =>\n  f(x)")
        assert result.errors == []

    def test_function_can_call_itself_with_expression(self):
        result = _resolve("f := (x) =>\n  f(x - 1)")
        assert result.errors == []

    def test_inline_function_self_reference_via_binding(self):
        result = _resolve("f := (x) => f(x)")
        assert result.errors == []


class TestUndefinedVariable:
    def test_undefined_identifier(self):
        result = _resolve("x")
        assert len(result.errors) == 1
        assert result.errors[0].kind == ResolveErrorKind.UNDEFINED_VARIABLE
        assert result.errors[0].name == "x"

    def test_forward_reference_is_error(self):
        result = _resolve("y := x + 1\nx := 5")
        assert any(e.kind == ResolveErrorKind.UNDEFINED_VARIABLE and e.name == "x" for e in result.errors)

    def test_undefined_function_call(self):
        result = _resolve("foo()")
        assert len(result.errors) == 1
        assert result.errors[0].kind == ResolveErrorKind.UNDEFINED_VARIABLE
        assert result.errors[0].name == "foo"

    def test_undefined_arg_in_function_call(self):
        result = _resolve("f := (x) =>\n  x\nf(missing)")
        assert any(e.kind == ResolveErrorKind.UNDEFINED_VARIABLE and e.name == "missing" for e in result.errors)

    def test_undefined_in_binary_op(self):
        result = _resolve("y := a + 1")
        assert any(e.kind == ResolveErrorKind.UNDEFINED_VARIABLE and e.name == "a" for e in result.errors)

    def test_undefined_in_list_literal(self):
        result = _resolve("z := [missing]")
        assert any(e.kind == ResolveErrorKind.UNDEFINED_VARIABLE and e.name == "missing" for e in result.errors)

    def test_undefined_in_for_loop_iterable(self):
        result = _resolve("for x in missing\n  x")
        assert any(e.kind == ResolveErrorKind.UNDEFINED_VARIABLE and e.name == "missing" for e in result.errors)

    def test_undefined_in_if_condition(self):
        result = _resolve("if flag\n  1")
        assert any(e.kind == ResolveErrorKind.UNDEFINED_VARIABLE and e.name == "flag" for e in result.errors)

    def test_param_not_visible_outside_function(self):
        result = _resolve("f := (x) =>\n  x\nx")
        assert any(e.kind == ResolveErrorKind.UNDEFINED_VARIABLE and e.name == "x" for e in result.errors)

    def test_for_loop_variable_not_visible_outside(self):
        result = _resolve("items := [1]\nfor i in items\n  i\ni")
        assert any(e.kind == ResolveErrorKind.UNDEFINED_VARIABLE and e.name == "i" for e in result.errors)


class TestDuplicateBinding:
    def test_duplicate_in_top_level(self):
        result = _resolve("x := 1\nx := 2")
        assert len(result.errors) == 1
        assert result.errors[0].kind == ResolveErrorKind.DUPLICATE_BINDING
        assert result.errors[0].name == "x"

    def test_duplicate_params_in_function(self):
        result = _resolve("f := (x, x) =>\n  x")
        assert any(e.kind == ResolveErrorKind.DUPLICATE_BINDING and e.name == "x" for e in result.errors)


class TestShadowedBinding:
    def test_binding_in_function_shadows_outer(self):
        result = _resolve("x := 1\nf := (x) =>\n  x")
        assert any(e.kind == ResolveErrorKind.SHADOWED_BINDING and e.name == "x" for e in result.errors)

    def test_binding_inside_function_body_shadows_outer(self):
        result = _resolve("x := 1\nf := () =>\n  x := 2\n  x")
        assert any(e.kind == ResolveErrorKind.SHADOWED_BINDING and e.name == "x" for e in result.errors)

    def test_for_loop_variable_shadows_outer(self):
        result = _resolve("x := 1\nfor x in [1, 2]\n  x")
        assert any(e.kind == ResolveErrorKind.SHADOWED_BINDING and e.name == "x" for e in result.errors)

    def test_if_branch_binding_shadows_outer(self):
        result = _resolve("x := 1\nif true\n  x := 2\n  x")
        assert any(e.kind == ResolveErrorKind.SHADOWED_BINDING and e.name == "x" for e in result.errors)


class TestNestedScopes:
    def test_nested_functions_no_shadowing(self):
        result = _resolve("outer := (a) =>\n  inner := (b) =>\n    a + b\n  inner(1)")
        assert result.errors == []

    def test_nested_functions_param_shadowing_is_error(self):
        result = _resolve("outer := (x) =>\n  inner := (x) =>\n    x\n  inner(1)")
        assert any(e.kind == ResolveErrorKind.SHADOWED_BINDING and e.name == "x" for e in result.errors)

    def test_inner_binding_can_reference_outer_param(self):
        result = _resolve("f := (a) =>\n  b := a + 1\n  b")
        assert result.errors == []

    def test_multiple_if_branches_get_separate_scopes(self):
        result = _resolve("flag := true\nif flag\n  a := 1\n  a\nelse\n  b := 2\n  b")
        assert result.errors == []


class TestEnvironmentAfterResolution:
    def test_top_level_binding_in_environment(self):
        result = _resolve("x := 5")
        assert result.environment.contains("x")

    def test_multiple_bindings_in_environment(self):
        result = _resolve("x := 1\ny := 2")
        assert result.environment.contains("x")
        assert result.environment.contains("y")

    def test_function_params_not_in_top_level_environment(self):
        result = _resolve("f := (x) =>\n  x")
        assert not result.environment.contains("x")
        assert result.environment.contains("f")
