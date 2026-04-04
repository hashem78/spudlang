from spud_fmt.config import FmtConfig
from tests.fmt.helpers import (
    bind,
    binop,
    call,
    fmt,
    funcdef,
    id,
    inline_funcdef,
    num,
    str_,
    unit,
)


class TestFunctionCall:
    def test_no_args(self):
        assert fmt().format_node(call("foo"), 0) == "foo()"

    def test_one_arg(self):
        assert fmt().format_node(call("foo", num(1)), 0) == "foo(1)"

    def test_multiple_args(self):
        assert fmt().format_node(call("foo", num(1), num(2)), 0) == "foo(1, 2)"

    def test_no_comma_space(self):
        cfg = FmtConfig(space_after_comma=False)
        assert fmt(cfg).format_node(call("foo", num(1), num(2)), 0) == "foo(1,2)"

    def test_string_arg(self):
        assert fmt().format_node(call("greet", str_("world")), 0) == "greet('world')"

    def test_expression_arg(self):
        arg = binop(id("a"), "+", id("b"))
        assert fmt().format_node(call("foo", arg), 0) == "foo(a + b)"

    def test_nested_call(self):
        inner = call("bar", num(1))
        assert fmt().format_node(call("foo", inner), 0) == "foo(bar(1))"


class TestFunctionDef:
    def test_single_param(self):
        result = fmt().format_node(funcdef(["x"], [id("x")]), 0)
        assert result == "(x: Int): Int =>\n  x"

    def test_multiple_params(self):
        result = fmt().format_node(funcdef(["a", "b", "c"], [id("a")]), 0)
        assert result == "(a: Int, b: Int, c: Int): Int =>\n  a"

    def test_no_comma_space(self):
        cfg = FmtConfig(space_after_comma=False)
        result = fmt(cfg).format_node(funcdef(["a", "b"], [id("a")]), 0)
        assert result.startswith("(a: Int,b: Int)")

    def test_no_fat_arrow_space(self):
        cfg = FmtConfig(spaces_around_fat_arrow=False)
        result = fmt(cfg).format_node(funcdef(["x"], [id("x")]), 0)
        assert result.startswith("(x: Int): Int=>")

    def test_nested_body(self):
        body = [bind("y", binop(id("x"), "+", num(1))), id("y")]
        result = fmt().format_node(funcdef(["x"], body), 0)
        lines = result.split("\n")
        assert len(lines) == 3


class TestInlineFunctionDef:
    def test_two_params(self):
        result = fmt().format_node(inline_funcdef(["a", "b"], binop(id("a"), "+", id("b"))), 0)
        assert result == "(a: Int, b: Int): Int => a + b"

    def test_single_param(self):
        result = fmt().format_node(inline_funcdef(["a"], id("a")), 0)
        assert result == "(a: Int): Int => a"

    def test_no_params(self):
        result = fmt().format_node(inline_funcdef([], num(42)), 0)
        assert result == "(): Int => 42"

    def test_void_callback(self):
        result = fmt().format_node(inline_funcdef([], unit()), 0)
        assert result == "(): Int => ()"

    def test_no_comma_space(self):
        cfg = FmtConfig(space_after_comma=False)
        result = fmt(cfg).format_node(inline_funcdef(["a", "b"], id("a")), 0)
        assert result == "(a: Int,b: Int): Int => a"

    def test_no_fat_arrow_space(self):
        cfg = FmtConfig(spaces_around_fat_arrow=False)
        result = fmt(cfg).format_node(inline_funcdef(["x"], id("x")), 0)
        assert result == "(x: Int): Int=>x"

    def test_body_with_binary_op(self):
        body = binop(id("x"), "*", binop(id("y"), "+", num(1)))
        result = fmt().format_node(inline_funcdef(["x", "y"], body), 0)
        assert result == "(x: Int, y: Int): Int => x * (y + 1)"

    def test_binding_inline_function(self):
        node = bind("add", inline_funcdef(["a", "b"], binop(id("a"), "+", id("b"))))
        result = fmt().format_node(node, 0)
        assert result == "add: Int := (a: Int, b: Int): Int => a + b"

    def test_binding_inline_not_block_node(self):
        from spud_fmt.formatters.body_fmt import is_block_node

        node = bind("f", inline_funcdef(["x"], id("x")))
        assert not is_block_node(node)

    def test_binding_block_function_is_block_node(self):
        from spud_fmt.formatters.body_fmt import is_block_node

        node = bind("f", funcdef(["x"], [id("x")]))
        assert is_block_node(node)


class TestUnitLiteral:
    def test_format(self):
        result = fmt().format_node(unit(), 0)
        assert result == "()"

    def test_in_binding(self):
        result = fmt().format_node(bind("x", unit()), 0)
        assert result == "x: Int := ()"
