from spud.stage_six.binding import Binding
from spud.stage_six.function_type_expr import FunctionTypeExpr
from spud.stage_six.list_type_expr import ListTypeExpr
from spud.stage_six.named_type import NamedType
from tests.stage_six.helpers import parse


class TestNamedTypes:
    def test_int(self):
        result = parse("x : Int := 1")
        node = result.body[0]
        assert isinstance(node, Binding)
        assert isinstance(node.type_annotation, NamedType)
        assert node.type_annotation.name == "Int"

    def test_float(self):
        result = parse("x : Float := 1.0")
        node = result.body[0]
        assert isinstance(node, Binding)
        assert isinstance(node.type_annotation, NamedType)
        assert node.type_annotation.name == "Float"

    def test_string(self):
        result = parse('x : String := "hello"')
        node = result.body[0]
        assert isinstance(node, Binding)
        assert isinstance(node.type_annotation, NamedType)
        assert node.type_annotation.name == "String"

    def test_bool(self):
        result = parse("x : Bool := true")
        node = result.body[0]
        assert isinstance(node, Binding)
        assert isinstance(node.type_annotation, NamedType)
        assert node.type_annotation.name == "Bool"

    def test_unit(self):
        result = parse("x : Unit := ()")
        node = result.body[0]
        assert isinstance(node, Binding)
        assert isinstance(node.type_annotation, NamedType)
        assert node.type_annotation.name == "Unit"


class TestListTypes:
    def test_list_of_int(self):
        result = parse("x : List[Int] := [1]")
        node = result.body[0]
        assert isinstance(node, Binding)
        assert isinstance(node.type_annotation, ListTypeExpr)
        assert isinstance(node.type_annotation.element, NamedType)
        assert node.type_annotation.element.name == "Int"

    def test_nested_list(self):
        result = parse("x : List[List[Int]] := [[1]]")
        node = result.body[0]
        assert isinstance(node, Binding)
        assert isinstance(node.type_annotation, ListTypeExpr)
        inner = node.type_annotation.element
        assert isinstance(inner, ListTypeExpr)
        assert isinstance(inner.element, NamedType)
        assert inner.element.name == "Int"


class TestFunctionTypes:
    def test_single_param(self):
        result = parse("f : Function[[Int], Int] := (x : Int) : Int =>\n  x + 1")
        node = result.body[0]
        assert isinstance(node, Binding)
        assert isinstance(node.type_annotation, FunctionTypeExpr)
        assert len(node.type_annotation.params) == 1
        assert isinstance(node.type_annotation.params[0], NamedType)
        assert node.type_annotation.params[0].name == "Int"
        assert isinstance(node.type_annotation.returns, NamedType)
        assert node.type_annotation.returns.name == "Int"

    def test_multiple_params(self):
        result = parse("f : Function[[Int, String], Bool] := (a : Int, b : String) : Bool =>\n  true")
        node = result.body[0]
        assert isinstance(node, Binding)
        assert isinstance(node.type_annotation, FunctionTypeExpr)
        assert len(node.type_annotation.params) == 2
        assert isinstance(node.type_annotation.params[0], NamedType)
        assert node.type_annotation.params[0].name == "Int"
        assert isinstance(node.type_annotation.params[1], NamedType)
        assert node.type_annotation.params[1].name == "String"
        assert isinstance(node.type_annotation.returns, NamedType)
        assert node.type_annotation.returns.name == "Bool"

    def test_no_params(self):
        result = parse("f : Function[[], Unit] := () : Unit =>\n  ()")
        node = result.body[0]
        assert isinstance(node, Binding)
        assert isinstance(node.type_annotation, FunctionTypeExpr)
        assert node.type_annotation.params == []
        assert isinstance(node.type_annotation.returns, NamedType)
        assert node.type_annotation.returns.name == "Unit"
