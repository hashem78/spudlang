from tests.fmt.helpers import (
    bind,
    binop,
    bool_,
    branch,
    call,
    fmt,
    forloop,
    id,
    ifelse,
    num,
    str_,
)


class TestIfElse:
    def test_if_only(self):
        node = ifelse([branch(binop(id("x"), ">", num(0)), [str_("positive")])])
        result = fmt().format_node(node, 0)
        assert result == "if x > 0\n  'positive'"

    def test_if_else(self):
        node = ifelse(
            [branch(binop(id("x"), ">", num(0)), [str_("positive")])],
            else_body=[str_("negative")],
        )
        result = fmt().format_node(node, 0)
        lines = result.split("\n")
        assert lines[0] == "if x > 0"
        assert lines[1] == "  'positive'"
        assert lines[2] == "else"
        assert lines[3] == "  'negative'"

    def test_if_elif_else(self):
        node = ifelse(
            [
                branch(binop(id("x"), ">", num(0)), [str_("positive")]),
                branch(binop(id("x"), "<", num(0)), [str_("negative")]),
            ],
            else_body=[str_("zero")],
        )
        result = fmt().format_node(node, 0)
        assert "if x > 0" in result
        assert "elif x < 0" in result
        assert "else" in result

    def test_nested_condition(self):
        cond = binop(binop(id("x"), ">", num(0)), "&&", binop(id("x"), "<", num(10)))
        node = ifelse([branch(cond, [str_("ok")])])
        result = fmt().format_node(node, 0)
        assert "x > 0 && x < 10" in result

    def test_multi_statement_body(self):
        node = ifelse([branch(bool_(True), [bind("x", num(1)), id("x")])])
        result = fmt().format_node(node, 0)
        lines = result.split("\n")
        assert len(lines) == 3

    def test_indented(self):
        node = ifelse([branch(bool_(True), [str_("yes")])])
        result = fmt().format_node(node, 1)
        assert result.startswith("  if")


class TestForLoop:
    def test_simple(self):
        node = forloop("x", id("items"), [call("print", id("x"))])
        result = fmt().format_node(node, 0)
        assert result == "for x: Int in items\n  print(x)"

    def test_function_call_iterable(self):
        node = forloop("i", call("range", num(10)), [call("print", id("i"))])
        result = fmt().format_node(node, 0)
        assert result == "for i: Int in range(10)\n  print(i)"

    def test_multi_statement_body(self):
        body = [bind("y", binop(id("x"), "*", num(2))), call("print", id("y"))]
        node = forloop("x", id("items"), body)
        result = fmt().format_node(node, 0)
        lines = result.split("\n")
        assert len(lines) == 3

    def test_nested_for(self):
        inner = forloop("j", id("cols"), [call("draw", id("i"), id("j"))])
        node = forloop("i", id("rows"), [inner])
        result = fmt().format_node(node, 0)
        assert "for i: Int in rows" in result
        assert "  for j: Int in cols" in result
        assert "    draw(i, j)" in result

    def test_indented(self):
        node = forloop("x", id("items"), [id("x")])
        result = fmt().format_node(node, 1)
        assert result.startswith("  for")
