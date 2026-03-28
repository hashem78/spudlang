from spud_fmt.config import FmtConfig

from tests.fmt.helpers import bind, bool_, fmt, funcdef, id, num, program


class TestConfigIndent:
    def test_indent_2(self):
        func = funcdef(["x"], [id("x")])
        result = fmt(FmtConfig(indent_size=2)).format_node(bind("f", func), 0)
        assert "\n  x" in result

    def test_indent_4(self):
        func = funcdef(["x"], [id("x")])
        result = fmt(FmtConfig(indent_size=4)).format_node(bind("f", func), 0)
        assert "\n    x" in result

    def test_indent_8(self):
        func = funcdef(["x"], [id("x")])
        result = fmt(FmtConfig(indent_size=8)).format_node(bind("f", func), 0)
        assert "\n        x" in result


class TestConfigBlankLines:
    def test_blank_lines_enabled(self):
        prog = program(bind("x", num(1)), bind("f", funcdef(["a"], [id("a")])))
        result = fmt().format_program(prog)
        assert "\n\n" in result

    def test_blank_lines_disabled(self):
        cfg = FmtConfig(blank_lines_around_blocks=False)
        prog = program(bind("x", num(1)), bind("f", funcdef(["a"], [id("a")])))
        result = fmt(cfg).format_program(prog)
        assert "\n\n" not in result


class TestConfigTrailingNewline:
    def test_trailing_newline_enabled(self):
        result = fmt().format_program(program(bind("x", num(1))))
        assert result.endswith("\n")

    def test_trailing_newline_disabled(self):
        cfg = FmtConfig(trailing_newline=False)
        result = fmt(cfg).format_program(program(bind("x", num(1))))
        assert not result.endswith("\n")
