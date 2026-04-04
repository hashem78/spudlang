from spud.core.string_reader import StringReader
from spud.core.types.float_type import FloatType
from spud.core.types.function_type import FunctionType
from spud.core.types.int_type import IntType
from spud.core.types.list_type import ListType
from spud.core.types.unit_type import UnitType
from spud.di.container import Container
from spud_check.type_check_result import TypeCheckResult
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
from spud_check.type_errors.type_mismatch_error import TypeMismatchError
from spud_check.type_errors.unary_operator_type_error import UnaryOperatorTypeError
from spud_check.type_errors.unknown_type_error import UnknownTypeError
from spud_check.typed_nodes.typed_binding import TypedBinding
from spud_check.typed_nodes.typed_function_def import TypedFunctionDef
from spud_check.typed_nodes.typed_inline_function_def import TypedInlineFunctionDef
from spud_check.typed_nodes.typed_int_literal import TypedIntLiteral
from spud_check.typed_nodes.typed_program import TypedProgram


def _check(text: str) -> TypeCheckResult:
    from spud_check.type_checker import TypeChecker

    container = Container()
    pipeline = container.pipeline()
    result = pipeline.run(StringReader(text))
    return TypeChecker().check(result.program)


class TestValidPrograms:
    def test_int_binding(self):
        result = _check("x : Int := 42")
        assert result.errors == []

    def test_float_binding(self):
        result = _check("pi : Float := 3.14")
        assert result.errors == []

    def test_string_binding(self):
        result = _check("name : String := 'hello'")
        assert result.errors == []

    def test_bool_binding(self):
        result = _check("flag : Bool := true")
        assert result.errors == []

    def test_unit_binding(self):
        result = _check("nothing : Unit := ()")
        assert result.errors == []

    def test_list_int_binding(self):
        result = _check("xs : List[Int] := [1, 2, 3]")
        assert result.errors == []

    def test_function_binding_and_call(self):
        result = _check("f : Function[[Int], Int] := (x : Int) : Int =>\n  x\nresult : Int := f(1)")
        assert result.errors == []

    def test_inline_function_binding(self):
        result = _check("double : Function[[Int], Int] := (x : Int) : Int => x * 2")
        assert result.errors == []

    def test_for_loop(self):
        result = _check("xs : List[Int] := [1, 2, 3]\nfor i : Int in xs\n  y : Int := i * 2")
        assert result.errors == []

    def test_if_else_matching_types(self):
        result = _check("flag : Bool := true\nif flag\n  1\nelse\n  2")
        assert result.errors == []

    def test_binary_op_int_addition(self):
        result = _check("x : Int := 1 + 2")
        assert result.errors == []

    def test_binary_op_float_addition(self):
        result = _check("y : Float := 1.0 + 2.0")
        assert result.errors == []

    def test_unary_op_negation(self):
        result = _check("x : Int := -1")
        assert result.errors == []

    def test_self_recursive_function(self):
        result = _check(
            "fact : Function[[Int], Int] := (n : Int) : Int =>\n  if n == 0\n    1\n  else\n    n * fact(n - 1)"
        )
        assert result.errors == []

    def test_empty_list_produces_no_errors(self):
        result = _check("xs : List[Unit] := []")
        assert result.errors == []

    def test_bool_operations(self):
        result = _check("x : Bool := true && false")
        assert result.errors == []

    def test_string_equality(self):
        result = _check("x : Bool := 'a' == 'b'")
        assert result.errors == []

    def test_int_comparison(self):
        result = _check("x : Bool := 1 < 2")
        assert result.errors == []

    def test_float_comparison(self):
        result = _check("x : Bool := 1.0 >= 2.0")
        assert result.errors == []

    def test_multi_param_function(self):
        result = _check(
            "add : Function[[Int, Int], Int] := (a : Int, b : Int) : Int =>\n  a + b\nresult : Int := add(1, 2)"
        )
        assert result.errors == []

    def test_function_using_outer_binding(self):
        result = _check("n : Int := 10\nf : Function[[Int], Int] := (x : Int) : Int =>\n  x + n")
        assert result.errors == []

    def test_unary_plus_on_int(self):
        result = _check("x : Int := +5")
        assert result.errors == []

    def test_unary_negation_float(self):
        result = _check("x : Float := -3.14")
        assert result.errors == []

    def test_nested_function(self):
        result = _check(
            "outer : Function[[Int], Int] := (a : Int) : Int =>\n"
            "  inner : Function[[Int], Int] := (b : Int) : Int =>\n"
            "    a + b\n"
            "  inner(1)"
        )
        assert result.errors == []


class TestTypeMismatch:
    def test_float_assigned_to_int(self):
        result = _check("x : Int := 3.14")
        assert len(result.errors) == 1
        assert isinstance(result.errors[0], TypeMismatchError)

    def test_int_assigned_to_string(self):
        result = _check("x : String := 42")
        assert len(result.errors) == 1
        assert isinstance(result.errors[0], TypeMismatchError)

    def test_int_assigned_to_bool(self):
        result = _check("x : Bool := 1")
        assert len(result.errors) == 1
        assert isinstance(result.errors[0], TypeMismatchError)

    def test_string_assigned_to_int(self):
        result = _check("x : Int := 'hello'")
        assert len(result.errors) == 1
        assert isinstance(result.errors[0], TypeMismatchError)

    def test_bool_assigned_to_float(self):
        result = _check("x : Float := false")
        assert len(result.errors) == 1
        assert isinstance(result.errors[0], TypeMismatchError)

    def test_mismatch_records_name(self):
        result = _check("myVar : Int := 3.14")
        assert any(isinstance(e, TypeMismatchError) and e.name == "myVar" for e in result.errors)


class TestOperatorTypeError:
    def test_mixed_arithmetic_float_int(self):
        result = _check("a : Float := 1.0\nb : Int := 2\nc : Float := a * b")
        assert any(isinstance(e, OperatorTypeError) for e in result.errors)

    def test_string_plus_int(self):
        result = _check("a : String := 'hi'\nb : Int := 1\nc : Int := a + b")
        assert any(isinstance(e, OperatorTypeError) for e in result.errors)

    def test_bool_arithmetic(self):
        result = _check("a : Bool := true\nb : Bool := false\nc : Int := a + b")
        assert any(isinstance(e, OperatorTypeError) for e in result.errors)

    def test_int_logical_and(self):
        result = _check("a : Int := 1\nb : Int := 2\nc : Bool := a && b")
        assert any(isinstance(e, OperatorTypeError) for e in result.errors)

    def test_operator_type_error_records_operator(self):
        result = _check("a : Float := 1.0\nb : Int := 2\nc : Float := a + b")
        errors = [e for e in result.errors if isinstance(e, OperatorTypeError)]
        assert len(errors) >= 1
        assert errors[0].operator == "+"


class TestUnaryOperatorTypeError:
    def test_negate_string(self):
        result = _check("x : String := 'hi'\ny : String := -x")
        assert any(isinstance(e, UnaryOperatorTypeError) for e in result.errors)

    def test_negate_bool(self):
        result = _check("x : Bool := true\ny : Bool := -x")
        assert any(isinstance(e, UnaryOperatorTypeError) for e in result.errors)

    def test_unary_plus_string(self):
        result = _check("x : String := 'hello'\ny : String := +x")
        assert any(isinstance(e, UnaryOperatorTypeError) for e in result.errors)


class TestFunctionCallErrors:
    def test_not_callable_non_function_value(self):
        result = _check("x : Int := 5\ny : Int := x(1)")
        assert any(isinstance(e, NotCallableError) for e in result.errors)

    def test_not_callable_records_name(self):
        result = _check("myVal : Int := 5\nresult : Int := myVal(1)")
        errors = [e for e in result.errors if isinstance(e, NotCallableError)]
        assert len(errors) == 1
        assert errors[0].name == "myVal"

    def test_argument_count_mismatch_too_many_args(self):
        result = _check("f : Function[[Int], Int] := (x : Int) : Int =>\n  x\ny : Int := f(1, 2)")
        assert any(isinstance(e, ArgumentCountMismatchError) for e in result.errors)

    def test_argument_count_mismatch_too_few_args(self):
        result = _check("f : Function[[Int, Int], Int] := (x : Int, y : Int) : Int =>\n  x + y\nresult : Int := f(1)")
        assert any(isinstance(e, ArgumentCountMismatchError) for e in result.errors)

    def test_argument_count_mismatch_records_counts(self):
        result = _check("f : Function[[Int], Int] := (x : Int) : Int =>\n  x\ny : Int := f(1, 2)")
        errors = [e for e in result.errors if isinstance(e, ArgumentCountMismatchError)]
        assert len(errors) == 1
        assert errors[0].expected_count == 1
        assert errors[0].actual_count == 2

    def test_argument_type_mismatch(self):
        result = _check("f : Function[[Int], Int] := (x : Int) : Int =>\n  x\ny : Int := f(3.14)")
        assert any(isinstance(e, ArgumentTypeMismatchError) for e in result.errors)

    def test_argument_type_mismatch_records_index(self):
        result = _check(
            "f : Function[[Int, Int], Int] := (a : Int, b : Int) : Int =>\n  a + b\nresult : Int := f(1, 3.14)"
        )
        errors = [e for e in result.errors if isinstance(e, ArgumentTypeMismatchError)]
        assert len(errors) == 1
        assert errors[0].index == 1


class TestReturnTypeMismatch:
    def test_function_body_returns_wrong_type(self):
        result = _check("f : Function[[Int], Float] := (x : Int) : Float =>\n  x")
        assert any(isinstance(e, ReturnTypeMismatchError) for e in result.errors)

    def test_inline_function_body_returns_wrong_type(self):
        result = _check("f : Function[[Int], Float] := (x : Int) : Float => x")
        assert any(isinstance(e, ReturnTypeMismatchError) for e in result.errors)

    def test_return_mismatch_records_kinds(self):
        result = _check("f : Function[[Int], Float] := (x : Int) : Float =>\n  x")
        errors = [e for e in result.errors if isinstance(e, ReturnTypeMismatchError)]
        assert len(errors) == 1
        assert errors[0].expected == FloatType().kind
        assert errors[0].actual == IntType().kind

    def test_function_returning_string_when_int_expected(self):
        result = _check("f : Function[[], Int] := () : Int =>\n  'oops'")
        assert any(isinstance(e, ReturnTypeMismatchError) for e in result.errors)


class TestBranchTypeMismatch:
    def test_if_else_branches_differ(self):
        result = _check("if true\n  1\nelse\n  'hello'")
        assert any(isinstance(e, BranchTypeMismatchError) for e in result.errors)

    def test_if_else_branch_mismatch_records_types(self):
        result = _check("if true\n  1\nelse\n  3.14")
        errors = [e for e in result.errors if isinstance(e, BranchTypeMismatchError)]
        assert len(errors) == 1
        assert errors[0].expected == IntType().kind
        assert errors[0].actual == FloatType().kind

    def test_elif_branch_type_mismatch(self):
        result = _check("if true\n  1\nelif false\n  2.0\nelse\n  3")
        assert any(isinstance(e, BranchTypeMismatchError) for e in result.errors)


class TestConditionNotBool:
    def test_int_condition(self):
        result = _check("if 42\n  1\nelse\n  2")
        assert any(isinstance(e, ConditionNotBoolError) for e in result.errors)

    def test_float_condition(self):
        result = _check("if 1.0\n  1\nelse\n  2")
        assert any(isinstance(e, ConditionNotBoolError) for e in result.errors)

    def test_string_condition(self):
        result = _check("if 'yes'\n  1\nelse\n  2")
        assert any(isinstance(e, ConditionNotBoolError) for e in result.errors)

    def test_condition_not_bool_records_actual_kind(self):
        result = _check("if 42\n  1\nelse\n  2")
        errors = [e for e in result.errors if isinstance(e, ConditionNotBoolError)]
        assert len(errors) == 1
        assert errors[0].actual == IntType().kind


class TestForLoopErrors:
    def test_not_iterable(self):
        result = _check("x : Int := 5\nfor i : Int in x\n  y : Int := i")
        assert any(isinstance(e, NotIterableError) for e in result.errors)

    def test_not_iterable_records_actual_kind(self):
        result = _check("x : Int := 5\nfor i : Int in x\n  y : Int := i")
        errors = [e for e in result.errors if isinstance(e, NotIterableError)]
        assert len(errors) == 1
        assert errors[0].actual == IntType().kind

    def test_element_type_mismatch(self):
        result = _check("xs : List[Int] := [1, 2]\nfor i : Float in xs\n  y : Float := i")
        assert any(isinstance(e, ElementTypeMismatchError) for e in result.errors)

    def test_element_type_mismatch_records_variable_name(self):
        result = _check("xs : List[Int] := [1, 2]\nfor myVar : Float in xs\n  y : Float := myVar")
        errors = [e for e in result.errors if isinstance(e, ElementTypeMismatchError)]
        assert len(errors) == 1
        assert errors[0].name == "myVar"

    def test_element_type_mismatch_records_kinds(self):
        result = _check("xs : List[Int] := [1, 2]\nfor i : Float in xs\n  y : Float := i")
        errors = [e for e in result.errors if isinstance(e, ElementTypeMismatchError)]
        assert len(errors) == 1
        assert errors[0].expected == FloatType().kind
        assert errors[0].actual == IntType().kind


class TestListErrors:
    def test_heterogeneous_list(self):
        result = _check("xs : List[Int] := [1, 3.14]")
        assert any(isinstance(e, HeterogeneousListError) for e in result.errors)

    def test_heterogeneous_list_records_index(self):
        result = _check("xs : List[Int] := [1, 3.14]")
        errors = [e for e in result.errors if isinstance(e, HeterogeneousListError)]
        assert len(errors) == 1
        assert errors[0].index == 1

    def test_heterogeneous_list_records_kinds(self):
        result = _check("xs : List[Int] := [1, 3.14]")
        errors = [e for e in result.errors if isinstance(e, HeterogeneousListError)]
        assert len(errors) == 1
        assert errors[0].expected == IntType().kind
        assert errors[0].actual == FloatType().kind

    def test_heterogeneous_list_multiple_mismatches(self):
        result = _check("xs : List[Int] := [1, 2.0, 'hello']")
        errors = [e for e in result.errors if isinstance(e, HeterogeneousListError)]
        assert len(errors) == 2

    def test_empty_list_no_errors(self):
        result = _check("xs : List[Unit] := []")
        assert not any(isinstance(e, HeterogeneousListError) for e in result.errors)


class TestUnknownType:
    def test_unknown_named_type(self):
        result = _check("x : Foo := 42")
        assert any(isinstance(e, UnknownTypeError) for e in result.errors)

    def test_unknown_type_records_name(self):
        result = _check("x : Banana := 42")
        errors = [e for e in result.errors if isinstance(e, UnknownTypeError)]
        assert len(errors) == 1
        assert errors[0].name == "Banana"

    def test_unknown_type_in_function_param(self):
        result = _check("f : Function[[Foo], Int] := (x : Foo) : Int =>\n  1")
        assert any(isinstance(e, UnknownTypeError) for e in result.errors)

    def test_unknown_return_type(self):
        result = _check("f : Function[[Int], Bar] := (x : Int) : Bar =>\n  x")
        assert any(isinstance(e, UnknownTypeError) for e in result.errors)


class TestTypedASTStructure:
    def test_int_binding_produces_typed_binding_with_int_type(self):
        result = _check("x : Int := 42")
        assert result.errors == []
        assert isinstance(result.typed_program, TypedProgram)
        node = result.typed_program.body[0]
        assert isinstance(node, TypedBinding)
        assert node.resolved_type == IntType()
        assert node.target_name == "x"

    def test_int_literal_value_inside_binding(self):
        result = _check("x : Int := 42")
        assert result.errors == []
        node = result.typed_program.body[0]
        assert isinstance(node, TypedBinding)
        assert isinstance(node.value, TypedIntLiteral)
        assert node.value.value == 42
        assert node.value.resolved_type == IntType()

    def test_function_binding_produces_function_type(self):
        result = _check("f : Function[[Int], Int] := (x : Int) : Int =>\n  x")
        assert result.errors == []
        node = result.typed_program.body[0]
        assert isinstance(node, TypedBinding)
        assert isinstance(node.resolved_type, FunctionType)
        assert node.resolved_type.params == (IntType(),)
        assert node.resolved_type.returns == IntType()

    def test_function_def_inside_binding(self):
        result = _check("f : Function[[Int], Int] := (x : Int) : Int =>\n  x")
        assert result.errors == []
        node = result.typed_program.body[0]
        assert isinstance(node, TypedBinding)
        assert isinstance(node.value, TypedFunctionDef)
        assert node.value.resolved_type == FunctionType(params=(IntType(),), returns=IntType())

    def test_inline_function_def_inside_binding(self):
        result = _check("double : Function[[Int], Int] := (x : Int) : Int => x * 2")
        assert result.errors == []
        node = result.typed_program.body[0]
        assert isinstance(node, TypedBinding)
        assert isinstance(node.value, TypedInlineFunctionDef)
        assert node.value.resolved_type == FunctionType(params=(IntType(),), returns=IntType())

    def test_typed_program_body_length(self):
        result = _check("x : Int := 1\ny : Float := 2.0")
        assert result.errors == []
        assert len(result.typed_program.body) == 2

    def test_empty_list_produces_list_of_unit(self):
        result = _check("xs : List[Unit] := []")
        assert result.errors == []
        node = result.typed_program.body[0]
        assert isinstance(node, TypedBinding)
        assert node.resolved_type == ListType(element=UnitType())

    def test_list_literal_resolved_type(self):
        result = _check("xs : List[Int] := [1, 2, 3]")
        assert result.errors == []
        node = result.typed_program.body[0]
        assert isinstance(node, TypedBinding)
        assert node.resolved_type == ListType(element=IntType())
