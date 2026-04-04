from spud.stage_six import (
    BinaryOp,
    Binding,
    ForLoop,
    FunctionCall,
    FunctionDef,
    Identifier,
    IfElse,
    IntLiteral,
    Program,
    StringLiteral,
    TypedParam,
)
from tests.stage_six.helpers import parse


class TestComplexPrograms:
    def test_binding_function_def_call(self):
        text = "add : Function[[Int, Int], Int] := (a : Int, b : Int) : Int =>\n  a + b\nresult : Int := add(1, 2)"
        result = parse(text)
        assert isinstance(result, Program)
        assert len(result.body) == 2
        assert isinstance(result.body[0], Binding)
        assert isinstance(result.body[0].value, FunctionDef)
        assert isinstance(result.body[1], Binding)
        assert isinstance(result.body[1].value, FunctionCall)
        assert result.body[1].value.callee.name == "add"

    def test_function_with_if_else_body(self):
        text = (
            "classify : Function[[Int], String] := (x : Int) : String =>\n"
            "  if x > 0\n"
            '    "positive"\n'
            "  else\n"
            '    "negative"'
        )
        result = parse(text)
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, Binding)
        fdef = node.value
        assert isinstance(fdef, FunctionDef)
        assert len(fdef.body) == 1
        assert isinstance(fdef.body[0], IfElse)
        assert len(fdef.body[0].branches) == 1
        assert fdef.body[0].else_body is not None

    def test_function_with_for_loop_body(self):
        text = (
            "looper : Function[[List[Int]], Unit] := (items : List[Int]) : Unit =>\n"
            "  for i : Int in items\n"
            "    process(i)"
        )
        result = parse(text)
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, Binding)
        fdef = node.value
        assert isinstance(fdef, FunctionDef)
        assert len(fdef.body) == 1
        assert isinstance(fdef.body[0], ForLoop)

    def test_deeply_nested(self):
        text = (
            "nested : Function[[Int], Unit] := (n : Int) : Unit =>\n"
            "  for i : Int in range(n)\n"
            "    if i > 5\n"
            "      print(i)"
        )
        result = parse(text)
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, Binding)
        fdef = node.value
        assert isinstance(fdef, FunctionDef)
        assert len(fdef.body) == 1
        for_loop = fdef.body[0]
        assert isinstance(for_loop, ForLoop)
        assert len(for_loop.body) == 1
        if_else = for_loop.body[0]
        assert isinstance(if_else, IfElse)
        assert len(if_else.branches) == 1
        call = if_else.branches[0].body[0]
        assert isinstance(call, FunctionCall)
        assert call.callee.name == "print"

    def test_multiple_top_level_statements(self):
        text = (
            "x : Int := 42\n"
            "greet : Function[[String], Unit] := (name : String) : Unit =>\n"
            "  print(name)\n"
            "for i : Int in range(x)\n"
            '  greet("hello")\n'
            "if x > 0\n"
            '  "positive"'
        )
        result = parse(text)
        assert isinstance(result, Program)
        assert len(result.body) == 4
        assert isinstance(result.body[0], Binding)
        assert isinstance(result.body[1], Binding)
        assert isinstance(result.body[1].value, FunctionDef)
        assert isinstance(result.body[2], ForLoop)
        assert isinstance(result.body[3], IfElse)

    def test_program_spud_pattern(self):
        text = (
            "nested : Function[[Int], String] := (n : Int) : String =>\n"
            "  for i : Int in range(n)\n"
            "    if i > 5\n"
            '      "big"\n'
            "    else\n"
            '      "small"'
        )
        result = parse(text)
        assert isinstance(result, Program)
        assert len(result.body) == 1
        node = result.body[0]
        assert isinstance(node, Binding)
        assert node.target.name == "nested"
        fdef = node.value
        assert isinstance(fdef, FunctionDef)
        assert len(fdef.params) == 1
        assert isinstance(fdef.params[0], TypedParam)
        assert fdef.params[0].name.name == "n"
        assert len(fdef.body) == 1
        for_loop = fdef.body[0]
        assert isinstance(for_loop, ForLoop)
        assert for_loop.variable.name == "i"
        assert isinstance(for_loop.iterable, FunctionCall)
        assert for_loop.iterable.callee.name == "range"
        assert len(for_loop.body) == 1
        if_else = for_loop.body[0]
        assert isinstance(if_else, IfElse)
        assert len(if_else.branches) == 1
        assert if_else.branches[0].condition.operator == ">"
        assert isinstance(if_else.branches[0].body[0], StringLiteral)
        assert if_else.branches[0].body[0].value == "big"
        assert if_else.else_body is not None
        assert isinstance(if_else.else_body[0], StringLiteral)
        assert if_else.else_body[0].value == "small"


class TestEdgeCases:
    def test_single_expression_program(self):
        result = parse("42")
        assert isinstance(result, Program)
        assert len(result.body) == 1
        assert isinstance(result.body[0], IntLiteral)
        assert result.body[0].value == 42

    def test_function_call_as_statement(self):
        result = parse('print("hello")')
        assert isinstance(result, Program)
        assert len(result.body) == 1
        node = result.body[0]
        assert isinstance(node, FunctionCall)
        assert node.callee.name == "print"
        assert len(node.args) == 1
        assert isinstance(node.args[0], StringLiteral)
        assert node.args[0].value == "hello"

    def test_all_precedence_levels(self):
        result = parse("a || b && c == d + e * f")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, BinaryOp)
        assert node.operator == "||"
        assert isinstance(node.left, Identifier)
        assert node.left.name == "a"
        rhs = node.right
        assert isinstance(rhs, BinaryOp)
        assert rhs.operator == "&&"
        assert isinstance(rhs.left, Identifier)
        assert rhs.left.name == "b"
        rhs2 = rhs.right
        assert isinstance(rhs2, BinaryOp)
        assert rhs2.operator == "=="
        assert isinstance(rhs2.left, Identifier)
        assert rhs2.left.name == "c"
        rhs3 = rhs2.right
        assert isinstance(rhs3, BinaryOp)
        assert rhs3.operator == "+"
        assert isinstance(rhs3.left, Identifier)
        assert rhs3.left.name == "d"
        rhs4 = rhs3.right
        assert isinstance(rhs4, BinaryOp)
        assert rhs4.operator == "*"
        assert isinstance(rhs4.left, Identifier)
        assert rhs4.left.name == "e"
        assert isinstance(rhs4.right, Identifier)
        assert rhs4.right.name == "f"

    def test_binding_to_grouped_expression(self):
        result = parse("x : Int := (a + b)")
        assert isinstance(result, Program)
        node = result.body[0]
        assert isinstance(node, Binding)
        assert node.target.name == "x"
        assert isinstance(node.value, BinaryOp)
        assert node.value.operator == "+"


class TestParseErrors:
    def test_unexpected_token_walrus_at_start(self):
        result = parse(":= 5")
        assert len(result.errors) > 0

    def test_missing_closing_paren(self):
        result = parse("foo(1")
        assert len(result.errors) > 0

    def test_missing_block_after_if(self):
        result = parse("if true")
        assert len(result.errors) > 0
