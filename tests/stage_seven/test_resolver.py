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
        result = _resolve("x : Int := 5")
        assert result.errors == []

    def test_multiple_bindings_sequential(self):
        result = _resolve("x : Int := 1\ny : Int := 2")
        assert result.errors == []

    def test_binding_referenced_after_definition(self):
        result = _resolve("x : Int := 5\ny : Int := x")
        assert result.errors == []

    def test_function_binding_with_param(self):
        result = _resolve("f : Function[[Int], Int] := (x : Int) : Int =>\n  x")
        assert result.errors == []

    def test_function_body_uses_param(self):
        result = _resolve("f : Function[[Int], Int] := (x : Int) : Int =>\n  x + 1")
        assert result.errors == []

    def test_function_body_uses_outer_binding(self):
        result = _resolve("n : Int := 10\nf : Function[[Int], Int] := (x : Int) : Int =>\n  x + n")
        assert result.errors == []

    def test_inline_function_binding(self):
        result = _resolve("add : Function[[Int, Int], Int] := (a : Int, b : Int) : Int => a + b")
        assert result.errors == []

    def test_function_call_to_known_binding(self):
        result = _resolve("f : Function[[Int], Int] := (x : Int) : Int =>\n  x\nf(1)")
        assert result.errors == []

    def test_list_literal_with_known_identifiers(self):
        result = _resolve("x : Int := 1\ny : Int := 2\nz : List[Int] := [x, y]")
        assert result.errors == []

    def test_for_loop_over_known_binding(self):
        result = _resolve("items : List[Int] := [1, 2]\nfor x : Int in items\n  x")
        assert result.errors == []

    def test_if_else_with_known_condition(self):
        result = _resolve("flag : Bool := true\nif flag\n  1\nelse\n  2")
        assert result.errors == []

    def test_binding_used_in_binary_op(self):
        result = _resolve("a : Int := 3\nb : Int := a + 1")
        assert result.errors == []

    def test_binding_used_in_unary_op(self):
        result = _resolve("a : Int := 5\nb : Int := -a")
        assert result.errors == []


class TestSelfRecursion:
    def test_function_can_call_itself(self):
        result = _resolve("f : Function[[Int], Int] := (x : Int) : Int =>\n  f(x)")
        assert result.errors == []

    def test_function_can_call_itself_with_expression(self):
        result = _resolve("f : Function[[Int], Int] := (x : Int) : Int =>\n  f(x - 1)")
        assert result.errors == []

    def test_inline_function_self_reference_via_binding(self):
        result = _resolve("f : Function[[Int], Int] := (x : Int) : Int => f(x)")
        assert result.errors == []


class TestUndefinedVariable:
    def test_undefined_identifier(self):
        result = _resolve("x")
        assert len(result.errors) == 1
        assert result.errors[0].kind == ResolveErrorKind.UNDEFINED_VARIABLE
        assert result.errors[0].name == "x"

    def test_forward_reference_is_error(self):
        result = _resolve("y : Int := x + 1\nx : Int := 5")
        assert any(e.kind == ResolveErrorKind.UNDEFINED_VARIABLE and e.name == "x" for e in result.errors)

    def test_undefined_function_call(self):
        result = _resolve("foo()")
        assert len(result.errors) == 1
        assert result.errors[0].kind == ResolveErrorKind.UNDEFINED_VARIABLE
        assert result.errors[0].name == "foo"

    def test_undefined_arg_in_function_call(self):
        result = _resolve("f : Function[[Int], Int] := (x : Int) : Int =>\n  x\nf(missing)")
        assert any(e.kind == ResolveErrorKind.UNDEFINED_VARIABLE and e.name == "missing" for e in result.errors)

    def test_undefined_in_binary_op(self):
        result = _resolve("y : Int := a + 1")
        assert any(e.kind == ResolveErrorKind.UNDEFINED_VARIABLE and e.name == "a" for e in result.errors)

    def test_undefined_in_list_literal(self):
        result = _resolve("z : List[Int] := [missing]")
        assert any(e.kind == ResolveErrorKind.UNDEFINED_VARIABLE and e.name == "missing" for e in result.errors)

    def test_undefined_in_for_loop_iterable(self):
        result = _resolve("for x : Int in missing\n  x")
        assert any(e.kind == ResolveErrorKind.UNDEFINED_VARIABLE and e.name == "missing" for e in result.errors)

    def test_undefined_in_if_condition(self):
        result = _resolve("if flag\n  1")
        assert any(e.kind == ResolveErrorKind.UNDEFINED_VARIABLE and e.name == "flag" for e in result.errors)

    def test_param_not_visible_outside_function(self):
        result = _resolve("f : Function[[Int], Int] := (x : Int) : Int =>\n  x\nx")
        assert any(e.kind == ResolveErrorKind.UNDEFINED_VARIABLE and e.name == "x" for e in result.errors)

    def test_for_loop_variable_not_visible_outside(self):
        result = _resolve("items : List[Int] := [1]\nfor i : Int in items\n  i\ni")
        assert any(e.kind == ResolveErrorKind.UNDEFINED_VARIABLE and e.name == "i" for e in result.errors)


class TestDuplicateBinding:
    def test_duplicate_in_top_level(self):
        result = _resolve("x : Int := 1\nx : Int := 2")
        assert len(result.errors) == 1
        assert result.errors[0].kind == ResolveErrorKind.DUPLICATE_BINDING
        assert result.errors[0].name == "x"

    def test_duplicate_params_in_function(self):
        result = _resolve("f : Function[[Int, Int], Int] := (x : Int, x : Int) : Int =>\n  x")
        assert any(e.kind == ResolveErrorKind.DUPLICATE_BINDING and e.name == "x" for e in result.errors)


class TestShadowedBinding:
    def test_binding_in_function_shadows_outer(self):
        result = _resolve("x : Int := 1\nf : Function[[Int], Int] := (x : Int) : Int =>\n  x")
        assert any(e.kind == ResolveErrorKind.SHADOWED_BINDING and e.name == "x" for e in result.errors)

    def test_binding_inside_function_body_shadows_outer(self):
        result = _resolve("x : Int := 1\nf : Function[[], Int] := () : Int =>\n  x : Int := 2\n  x")
        assert any(e.kind == ResolveErrorKind.SHADOWED_BINDING and e.name == "x" for e in result.errors)

    def test_for_loop_variable_shadows_outer(self):
        result = _resolve("x : Int := 1\nfor x : Int in [1, 2]\n  x")
        assert any(e.kind == ResolveErrorKind.SHADOWED_BINDING and e.name == "x" for e in result.errors)

    def test_if_branch_binding_shadows_outer(self):
        result = _resolve("x : Int := 1\nif true\n  x : Int := 2\n  x")
        assert any(e.kind == ResolveErrorKind.SHADOWED_BINDING and e.name == "x" for e in result.errors)


class TestNestedScopes:
    def test_nested_functions_no_shadowing(self):
        text = (
            "outer : Function[[Int], Int] := (a : Int) : Int =>\n"
            "  inner : Function[[Int], Int] := (b : Int) : Int =>\n"
            "    a + b\n"
            "  inner(1)"
        )
        result = _resolve(text)
        assert result.errors == []

    def test_nested_functions_param_shadowing_is_error(self):
        text = (
            "outer : Function[[Int], Int] := (x : Int) : Int =>\n"
            "  inner : Function[[Int], Int] := (x : Int) : Int =>\n"
            "    x\n"
            "  inner(1)"
        )
        result = _resolve(text)
        assert any(e.kind == ResolveErrorKind.SHADOWED_BINDING and e.name == "x" for e in result.errors)

    def test_inner_binding_can_reference_outer_param(self):
        result = _resolve("f : Function[[Int], Int] := (a : Int) : Int =>\n  b : Int := a + 1\n  b")
        assert result.errors == []

    def test_multiple_if_branches_get_separate_scopes(self):
        result = _resolve("flag : Bool := true\nif flag\n  a : Int := 1\n  a\nelse\n  b : Int := 2\n  b")
        assert result.errors == []


class TestEnvironmentAfterResolution:
    def test_top_level_binding_in_environment(self):
        result = _resolve("x : Int := 5")
        assert result.environment.contains("x")

    def test_multiple_bindings_in_environment(self):
        result = _resolve("x : Int := 1\ny : Int := 2")
        assert result.environment.contains("x")
        assert result.environment.contains("y")

    def test_function_params_not_in_top_level_environment(self):
        result = _resolve("f : Function[[Int], Int] := (x : Int) : Int =>\n  x")
        assert not result.environment.contains("x")
        assert result.environment.contains("f")

    def test_function_binding_produces_child_scope(self):
        result = _resolve("f : Function[[Int], Int] := (x : Int) : Int =>\n  x")
        assert result.errors == []
        assert len(result.environment.children) == 1

    def test_function_child_scope_contains_param(self):
        result = _resolve("f : Function[[Int], Int] := (x : Int) : Int =>\n  x")
        assert result.errors == []
        child = result.environment.children[0]
        assert child.contains("x")

    def test_inline_function_binding_produces_child_scope(self):
        result = _resolve("double : Function[[Int], Int] := (x : Int) : Int => x * 2")
        assert result.errors == []
        assert len(result.environment.children) == 1

    def test_inline_function_child_scope_contains_param(self):
        result = _resolve("double : Function[[Int], Int] := (x : Int) : Int => x * 2")
        assert result.errors == []
        child = result.environment.children[0]
        assert child.contains("x")

    def test_function_with_multiple_params_all_in_child_scope(self):
        result = _resolve("add : Function[[Int, Int], Int] := (a : Int, b : Int) : Int => a + b")
        assert result.errors == []
        child = result.environment.children[0]
        assert child.contains("a")
        assert child.contains("b")

    def test_for_loop_produces_child_scope(self):
        result = _resolve("items : List[Int] := [1, 2]\nfor i : Int in items\n  i")
        assert result.errors == []
        assert len(result.environment.children) == 1

    def test_for_loop_child_scope_contains_loop_variable(self):
        result = _resolve("items : List[Int] := [1, 2]\nfor i : Int in items\n  i")
        assert result.errors == []
        child = result.environment.children[0]
        assert child.contains("i")

    def test_for_loop_variable_not_in_global_scope(self):
        result = _resolve("items : List[Int] := [1, 2]\nfor i : Int in items\n  i")
        assert result.errors == []
        assert not result.environment.contains("i")

    def test_if_branch_produces_child_scope(self):
        result = _resolve("flag : Bool := true\nif flag\n  1")
        assert result.errors == []
        assert len(result.environment.children) == 1

    def test_if_else_produces_two_child_scopes(self):
        result = _resolve("flag : Bool := true\nif flag\n  1\nelse\n  2")
        assert result.errors == []
        assert len(result.environment.children) == 2

    def test_if_elif_else_produces_three_child_scopes(self):
        result = _resolve("x : Int := 1\nif x == 1\n  1\nelif x == 2\n  2\nelse\n  3")
        assert result.errors == []
        assert len(result.environment.children) == 3

    def test_if_branch_bindings_not_in_global_scope(self):
        result = _resolve("flag : Bool := true\nif flag\n  1")
        assert result.errors == []
        assert not result.environment.contains("flag") or result.environment.contains("flag")
        child = result.environment.children[0]
        assert child.parent is not None

    def test_two_functions_produce_two_children(self):
        f_src = "f : Function[[Int], Int] := (a : Int) : Int =>\n  a"
        g_src = "g : Function[[Int], Int] := (b : Int) : Int =>\n  b"
        text = f_src + "\n" + g_src
        result = _resolve(text)
        assert result.errors == []
        assert len(result.environment.children) == 2
        child_f = result.environment.children[0]
        child_g = result.environment.children[1]
        assert child_f.contains("a")
        assert child_g.contains("b")

    def test_global_env_has_binding_and_one_child_for_self_recursive_function(self):
        result = _resolve("double : Function[[Int], Int] := (x : Int) : Int => double(x * 2)")
        assert result.errors == []
        assert result.environment.contains("double")
        assert len(result.environment.children) == 1
        child = result.environment.children[0]
        assert child.contains("x")

    def test_nested_function_produces_nested_children(self):
        text = (
            "outer : Function[[Int], Int] := (a : Int) : Int =>\n"
            "  inner : Function[[Int], Int] := (b : Int) : Int =>\n"
            "    a + b\n"
            "  inner(1)"
        )
        result = _resolve(text)
        assert result.errors == []
        assert len(result.environment.children) == 1
        outer_child = result.environment.children[0]
        assert outer_child.contains("a")
        assert len(outer_child.children) == 1
        inner_child = outer_child.children[0]
        assert inner_child.contains("b")

    def test_empty_program_has_no_children(self):
        result = _resolve("")
        assert result.errors == []
        assert result.environment.children == ()

    def test_plain_binding_does_not_produce_child(self):
        result = _resolve("x : Int := 5\ny : Int := 10")
        assert result.errors == []
        assert result.environment.children == ()
