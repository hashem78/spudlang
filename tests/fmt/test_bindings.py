from spud_fmt import FmtConfig
from tests.fmt.helpers import bind, binop, bool_, call, fmt, funcdef, id, num, str_


class TestBinding:
    def test_simple_numeric(self):
        assert fmt().format_node(bind("x", num(1)), 0) == "x: Int := 1"

    def test_string(self):
        assert fmt().format_node(bind("name", str_("spud")), 0) == "name: Int := 'spud'"

    def test_boolean(self):
        assert fmt().format_node(bind("flag", bool_(True)), 0) == "flag: Int := true"

    def test_binary_op(self):
        assert fmt().format_node(bind("x", binop(id("a"), "+", id("b"))), 0) == "x: Int := a + b"

    def test_function_call(self):
        assert fmt().format_node(bind("x", call("foo", num(1))), 0) == "x: Int := foo(1)"

    def test_no_walrus_spaces(self):
        cfg = FmtConfig(spaces_around_walrus=False)
        assert fmt(cfg).format_node(bind("x", num(1)), 0) == "x: Int:=1"

    def test_function_def_value(self):
        func = funcdef(["a", "b"], [id("a")])
        result = fmt().format_node(bind("add", func), 0)
        assert result == "add: Int := (a: Int, b: Int): Int =>\n  a"

    def test_function_def_multi_body(self):
        func = funcdef(["x"], [bind("y", binop(id("x"), "+", num(1))), id("y")])
        result = fmt().format_node(bind("f", func), 0)
        lines = result.split("\n")
        assert lines[0] == "f: Int := (x: Int): Int =>"
        assert lines[1] == "  y: Int := x + 1"
        assert lines[2] == "  y"

    def test_indented_binding(self):
        result = fmt().format_node(bind("x", num(1)), 1)
        assert result == "  x: Int := 1"
