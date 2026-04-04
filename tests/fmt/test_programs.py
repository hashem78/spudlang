from tests.fmt.helpers import (
    bind,
    binop,
    bool_,
    branch,
    call,
    fmt,
    forloop,
    funcdef,
    id,
    ifelse,
    num,
    program,
    str_,
)


class TestFormatProgram:
    def test_empty_program(self):
        assert fmt().format_program(program()) == ""

    def test_single_statement(self):
        result = fmt().format_program(program(bind("x", num(1))))
        assert result == "x : Int := 1\n"

    def test_multiple_flat(self):
        prog = program(bind("x", num(1)), bind("y", num(2)), bind("z", num(3)))
        result = fmt().format_program(prog)
        assert result == "x : Int := 1\ny : Int := 2\nz : Int := 3\n"

    def test_blank_line_before_function_def(self):
        prog = program(bind("x", num(1)), bind("f", funcdef(["a"], [id("a")])))
        result = fmt().format_program(prog)
        lines = result.strip().split("\n")
        assert lines[1] == ""

    def test_blank_line_before_if(self):
        prog = program(bind("x", num(1)), ifelse([branch(bool_(True), [id("x")])]))
        result = fmt().format_program(prog)
        assert "\n\n" in result

    def test_blank_line_before_for(self):
        prog = program(bind("x", num(1)), forloop("i", id("items"), [id("i")]))
        result = fmt().format_program(prog)
        assert "\n\n" in result

    def test_blank_line_after_block(self):
        prog = program(
            bind("f", funcdef(["x"], [id("x")])),
            bind("y", num(42)),
        )
        result = fmt().format_program(prog)
        assert "\n\n" in result


class TestComplexPrograms:
    def test_fizzbuzz(self):
        body = [
            ifelse(
                [
                    branch(binop(binop(id("i"), "%", num(15)), "==", num(0)), [str_("fizzbuzz")]),
                    branch(binop(binop(id("i"), "%", num(3)), "==", num(0)), [str_("fizz")]),
                    branch(binop(binop(id("i"), "%", num(5)), "==", num(0)), [str_("buzz")]),
                ],
            )
        ]
        func = funcdef(["i"], body)
        prog = program(bind("fizzbuzz", func))
        result = fmt().format_program(prog)
        assert "fizzbuzz : Int := (i : Int) : Int =>" in result
        assert "if i % 15 == 0" in result
        assert "'fizzbuzz'" in result
        assert "elif i % 3 == 0" in result
        assert "elif i % 5 == 0" in result

    def test_nested_everything(self):
        prog = program(
            bind("max", num(100)),
            bind(
                "validate",
                funcdef(
                    ["input"],
                    [
                        ifelse(
                            [
                                branch(binop(id("input"), ">", num(0)), [str_("positive")]),
                                branch(binop(id("input"), "<", num(0)), [str_("negative")]),
                            ],
                            else_body=[str_("zero")],
                        )
                    ],
                ),
            ),
            forloop("i", call("range", id("max")), [call("validate", id("i"))]),
        )
        result = fmt().format_program(prog)
        assert "max : Int := 100" in result
        assert "validate : Int := (input : Int) : Int =>" in result
        assert "  if input > 0" in result
        assert "  elif input < 0" in result
        assert "  else" in result
        assert "for i : Int in range(max)" in result
        assert "  validate(i)" in result
