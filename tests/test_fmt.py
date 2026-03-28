# SPDX-FileCopyrightText: 2026-present hashem78 <hashem.olayano@gmail.com>
#
# SPDX-License-Identifier: MIT

from spud.core.position import Position
from spud.stage_six.binary_op import BinaryOp
from spud.stage_six.binding import Binding
from spud.stage_six.boolean_literal import BooleanLiteral
from spud.stage_six.condition_branch import ConditionBranch
from spud.stage_six.for_loop import ForLoop
from spud.stage_six.function_call import FunctionCall
from spud.stage_six.function_def import FunctionDef
from spud.stage_six.identifier import Identifier
from spud.stage_six.if_else import IfElse
from spud.stage_six.numeric_literal import NumericLiteral
from spud.stage_six.program import Program
from spud.stage_six.raw_string_literal import RawStringLiteral
from spud.stage_six.string_literal import StringLiteral
from spud.stage_six.unary_op import UnaryOp
from spud_fmt.config import FmtConfig, QuoteStyle
from spud_fmt.container import _create_formatter
from spud_fmt.formatter import Formatter

P = Position(line=0, column=0)


def _fmt(config: FmtConfig | None = None) -> Formatter:
    return _create_formatter(config or FmtConfig())


def _id(name: str) -> Identifier:
    return Identifier(position=P, end=P, name=name)


def _num(value: int) -> NumericLiteral:
    return NumericLiteral(position=P, end=P, value=value)


def _str(value: str) -> StringLiteral:
    return StringLiteral(position=P, end=P, value=value)


def _raw(value: str) -> RawStringLiteral:
    return RawStringLiteral(position=P, end=P, value=value)


def _bool(value: bool) -> BooleanLiteral:
    return BooleanLiteral(position=P, end=P, value=value)


def _binop(left, op: str, right) -> BinaryOp:
    return BinaryOp(position=P, end=P, left=left, operator=op, right=right)


def _neg(operand) -> UnaryOp:
    return UnaryOp(position=P, end=P, operator="-", operand=operand)


def _pos(operand) -> UnaryOp:
    return UnaryOp(position=P, end=P, operator="+", operand=operand)


def _call(name: str, *args) -> FunctionCall:
    return FunctionCall(position=P, end=P, callee=_id(name), args=list(args))


def _bind(name: str, value) -> Binding:
    return Binding(position=P, end=P, target=_id(name), value=value)


def _funcdef(params: list[str], body: list) -> FunctionDef:
    return FunctionDef(position=P, end=P, params=[_id(p) for p in params], body=body)


def _branch(condition, body: list) -> ConditionBranch:
    return ConditionBranch(position=P, end=P, condition=condition, body=body)


def _ifelse(branches: list, else_body=None) -> IfElse:
    return IfElse(position=P, end=P, branches=branches, else_body=else_body)


def _forloop(var: str, iterable, body: list) -> ForLoop:
    return ForLoop(position=P, end=P, variable=_id(var), iterable=iterable, body=body)


def _program(*body) -> Program:
    return Program(position=P, end=P, body=list(body))


# ── Identifier ───────────────────────────────────────────────────────


class TestIdentifier:
    def test_simple(self):
        assert _fmt().format_node(_id("x"), 0) == "x"

    def test_underscore(self):
        assert _fmt().format_node(_id("my_var"), 0) == "my_var"

    def test_single_char(self):
        assert _fmt().format_node(_id("a"), 0) == "a"


# ── Numeric ──────────────────────────────────────────────────────────


class TestNumeric:
    def test_zero(self):
        assert _fmt().format_node(_num(0), 0) == "0"

    def test_one(self):
        assert _fmt().format_node(_num(1), 0) == "1"

    def test_large(self):
        assert _fmt().format_node(_num(999999), 0) == "999999"


# ── String ───────────────────────────────────────────────────────────


class TestString:
    def test_simple_single_quotes(self):
        assert _fmt().format_node(_str("hello"), 0) == "'hello'"

    def test_simple_double_quotes(self):
        cfg = FmtConfig(quote_style=QuoteStyle.DOUBLE)
        assert _fmt(cfg).format_node(_str("hello"), 0) == '"hello"'

    def test_escape_single_quote(self):
        assert _fmt().format_node(_str("it's"), 0) == "'it\\'s'"

    def test_escape_double_quote(self):
        cfg = FmtConfig(quote_style=QuoteStyle.DOUBLE)
        assert _fmt(cfg).format_node(_str('say "hi"'), 0) == '"say \\"hi\\""'

    def test_escape_backslash(self):
        assert _fmt().format_node(_str("a\\b"), 0) == "'a\\\\b'"

    def test_empty(self):
        assert _fmt().format_node(_str(""), 0) == "''"


# ── Raw String ───────────────────────────────────────────────────────


class TestRawString:
    def test_simple(self):
        assert _fmt().format_node(_raw("hello"), 0) == "`hello`"

    def test_with_quotes(self):
        assert _fmt().format_node(_raw('say "hi"'), 0) == '`say "hi"`'

    def test_with_newline(self):
        assert _fmt().format_node(_raw("a\nb"), 0) == "`a\nb`"

    def test_empty(self):
        assert _fmt().format_node(_raw(""), 0) == "``"


# ── Boolean ──────────────────────────────────────────────────────────


class TestBoolean:
    def test_true(self):
        assert _fmt().format_node(_bool(True), 0) == "true"

    def test_false(self):
        assert _fmt().format_node(_bool(False), 0) == "false"


# ── Binary Op ────────────────────────────────────────────────────────


class TestBinaryOp:
    def test_simple(self):
        assert _fmt().format_node(_binop(_id("a"), "+", _id("b")), 0) == "a + b"

    def test_no_spaces(self):
        cfg = FmtConfig(spaces_around_operators=False)
        assert _fmt(cfg).format_node(_binop(_id("a"), "+", _id("b")), 0) == "a+b"

    def test_chained_same_precedence(self):
        node = _binop(_id("a"), "+", _binop(_id("b"), "+", _id("c")))
        assert _fmt().format_node(node, 0) == "a + b + c"

    def test_higher_precedence_no_parens(self):
        node = _binop(_id("a"), "+", _binop(_id("b"), "*", _id("c")))
        assert _fmt().format_node(node, 0) == "a + b * c"

    def test_lower_precedence_needs_parens(self):
        node = _binop(_binop(_id("a"), "+", _id("b")), "*", _id("c"))
        assert _fmt().format_node(node, 0) == "(a + b) * c"

    def test_comparison(self):
        assert _fmt().format_node(_binop(_id("x"), "==", _num(5)), 0) == "x == 5"

    def test_logical_and(self):
        assert _fmt().format_node(_binop(_id("a"), "&&", _id("b")), 0) == "a && b"

    def test_logical_or(self):
        assert _fmt().format_node(_binop(_id("a"), "||", _id("b")), 0) == "a || b"

    def test_modulo(self):
        assert _fmt().format_node(_binop(_id("i"), "%", _num(15)), 0) == "i % 15"

    def test_mixed_precedence(self):
        # a + b * c - d  →  a + b * c - d (no parens needed, left to right)
        inner = _binop(_id("b"), "*", _id("c"))
        left = _binop(_id("a"), "+", inner)
        node = _binop(left, "-", _id("d"))
        result = _fmt().format_node(node, 0)
        assert "a + b * c" in result

    def test_all_operators(self):
        for op in ["+", "-", "*", "/", "%", "==", "!=", "<", ">", "<=", ">=", "&&", "||"]:
            result = _fmt().format_node(_binop(_id("a"), op, _id("b")), 0)
            assert f"a {op} b" == result


# ── Unary Op ─────────────────────────────────────────────────────────


class TestUnaryOp:
    def test_negative_number(self):
        assert _fmt().format_node(_neg(_num(5)), 0) == "-5"

    def test_negative_identifier(self):
        assert _fmt().format_node(_neg(_id("x")), 0) == "-x"

    def test_double_negation_collapses(self):
        assert _fmt().format_node(_neg(_neg(_id("x"))), 0) == "x"

    def test_triple_negation_collapses(self):
        assert _fmt().format_node(_neg(_neg(_neg(_id("x")))), 0) == "-x"

    def test_quad_negation_collapses(self):
        assert _fmt().format_node(_neg(_neg(_neg(_neg(_id("x"))))), 0) == "x"

    def test_negative_expression(self):
        assert _fmt().format_node(_neg(_binop(_id("a"), "+", _id("b"))), 0) == "-(a + b)"

    def test_negative_function_call(self):
        assert _fmt().format_node(_neg(_call("foo", _num(1))), 0) == "-foo(1)"

    def test_binding_to_negative(self):
        assert _fmt().format_node(_bind("x", _neg(_num(5))), 0) == "x := -5"

    def test_unary_plus(self):
        assert _fmt().format_node(_pos(_num(5)), 0) == "+5"

    def test_unary_plus_collapses_to_one(self):
        assert _fmt().format_node(_pos(_pos(_id("x"))), 0) == "+x"

    def test_unary_plus_triple(self):
        assert _fmt().format_node(_pos(_pos(_pos(_id("x")))), 0) == "+x"

    def test_plus_minus(self):
        assert _fmt().format_node(_pos(_neg(_id("x"))), 0) == "-x"

    def test_minus_plus(self):
        assert _fmt().format_node(_neg(_pos(_id("x"))), 0) == "-x"

    def test_plus_plus_minus(self):
        assert _fmt().format_node(_pos(_pos(_neg(_id("x")))), 0) == "-x"

    def test_minus_minus_plus(self):
        assert _fmt().format_node(_neg(_neg(_pos(_id("x")))), 0) == "+x"

    def test_plus_minus_minus(self):
        assert _fmt().format_node(_pos(_neg(_neg(_id("x")))), 0) == "+x"

    def test_collapse_unary_plus_config(self):
        cfg = FmtConfig(collapse_unary_plus=True)
        assert _fmt(cfg).format_node(_pos(_num(5)), 0) == "5"

    def test_collapse_unary_plus_config_double(self):
        cfg = FmtConfig(collapse_unary_plus=True)
        assert _fmt(cfg).format_node(_pos(_pos(_id("x"))), 0) == "x"

    def test_collapse_unary_plus_neg_still_works(self):
        cfg = FmtConfig(collapse_unary_plus=True)
        assert _fmt(cfg).format_node(_neg(_num(5)), 0) == "-5"

    def test_unary_plus_on_binary_op(self):
        assert _fmt().format_node(_pos(_binop(_id("a"), "+", _id("b"))), 0) == "+(a + b)"


# ── Function Call ────────────────────────────────────────────────────


class TestFunctionCall:
    def test_no_args(self):
        assert _fmt().format_node(_call("foo"), 0) == "foo()"

    def test_one_arg(self):
        assert _fmt().format_node(_call("foo", _num(1)), 0) == "foo(1)"

    def test_multiple_args(self):
        assert _fmt().format_node(_call("foo", _num(1), _num(2)), 0) == "foo(1, 2)"

    def test_no_comma_space(self):
        cfg = FmtConfig(space_after_comma=False)
        assert _fmt(cfg).format_node(_call("foo", _num(1), _num(2)), 0) == "foo(1,2)"

    def test_string_arg(self):
        assert _fmt().format_node(_call("greet", _str("world")), 0) == "greet('world')"

    def test_expression_arg(self):
        arg = _binop(_id("a"), "+", _id("b"))
        assert _fmt().format_node(_call("foo", arg), 0) == "foo(a + b)"

    def test_nested_call(self):
        inner = _call("bar", _num(1))
        assert _fmt().format_node(_call("foo", inner), 0) == "foo(bar(1))"


# ── Binding ──────────────────────────────────────────────────────────


class TestBinding:
    def test_simple_numeric(self):
        assert _fmt().format_node(_bind("x", _num(1)), 0) == "x := 1"

    def test_string(self):
        assert _fmt().format_node(_bind("name", _str("spud")), 0) == "name := 'spud'"

    def test_boolean(self):
        assert _fmt().format_node(_bind("flag", _bool(True)), 0) == "flag := true"

    def test_binary_op(self):
        assert _fmt().format_node(_bind("x", _binop(_id("a"), "+", _id("b"))), 0) == "x := a + b"

    def test_function_call(self):
        assert _fmt().format_node(_bind("x", _call("foo", _num(1))), 0) == "x := foo(1)"

    def test_no_walrus_spaces(self):
        cfg = FmtConfig(spaces_around_walrus=False)
        assert _fmt(cfg).format_node(_bind("x", _num(1)), 0) == "x:=1"

    def test_function_def_value(self):
        func = _funcdef(["a", "b"], [_id("a")])
        result = _fmt().format_node(_bind("add", func), 0)
        assert result == "add := (a, b) =>\n  a"

    def test_function_def_multi_body(self):
        func = _funcdef(["x"], [_bind("y", _binop(_id("x"), "+", _num(1))), _id("y")])
        result = _fmt().format_node(_bind("f", func), 0)
        lines = result.split("\n")
        assert lines[0] == "f := (x) =>"
        assert lines[1] == "  y := x + 1"
        assert lines[2] == "  y"

    def test_indented_binding(self):
        result = _fmt().format_node(_bind("x", _num(1)), 1)
        assert result == "  x := 1"


# ── Function Def ─────────────────────────────────────────────────────


class TestFunctionDef:
    def test_single_param(self):
        result = _fmt().format_node(_funcdef(["x"], [_id("x")]), 0)
        assert result == "(x) =>\n  x"

    def test_multiple_params(self):
        result = _fmt().format_node(_funcdef(["a", "b", "c"], [_id("a")]), 0)
        assert result == "(a, b, c) =>\n  a"

    def test_no_comma_space(self):
        cfg = FmtConfig(space_after_comma=False)
        result = _fmt(cfg).format_node(_funcdef(["a", "b"], [_id("a")]), 0)
        assert result.startswith("(a,b)")

    def test_no_fat_arrow_space(self):
        cfg = FmtConfig(spaces_around_fat_arrow=False)
        result = _fmt(cfg).format_node(_funcdef(["x"], [_id("x")]), 0)
        assert result.startswith("(x)=>")

    def test_nested_body(self):
        body = [_bind("y", _binop(_id("x"), "+", _num(1))), _id("y")]
        result = _fmt().format_node(_funcdef(["x"], body), 0)
        lines = result.split("\n")
        assert len(lines) == 3


# ── If/Else ──────────────────────────────────────────────────────────


class TestIfElse:
    def test_if_only(self):
        node = _ifelse([_branch(_binop(_id("x"), ">", _num(0)), [_str("positive")])])
        result = _fmt().format_node(node, 0)
        assert result == "if x > 0\n  'positive'"

    def test_if_else(self):
        node = _ifelse(
            [_branch(_binop(_id("x"), ">", _num(0)), [_str("positive")])],
            else_body=[_str("negative")],
        )
        result = _fmt().format_node(node, 0)
        lines = result.split("\n")
        assert lines[0] == "if x > 0"
        assert lines[1] == "  'positive'"
        assert lines[2] == "else"
        assert lines[3] == "  'negative'"

    def test_if_elif_else(self):
        node = _ifelse(
            [
                _branch(_binop(_id("x"), ">", _num(0)), [_str("positive")]),
                _branch(_binop(_id("x"), "<", _num(0)), [_str("negative")]),
            ],
            else_body=[_str("zero")],
        )
        result = _fmt().format_node(node, 0)
        assert "if x > 0" in result
        assert "elif x < 0" in result
        assert "else" in result

    def test_nested_condition(self):
        cond = _binop(_binop(_id("x"), ">", _num(0)), "&&", _binop(_id("x"), "<", _num(10)))
        node = _ifelse([_branch(cond, [_str("ok")])])
        result = _fmt().format_node(node, 0)
        assert "x > 0 && x < 10" in result

    def test_multi_statement_body(self):
        node = _ifelse([_branch(_bool(True), [_bind("x", _num(1)), _id("x")])])
        result = _fmt().format_node(node, 0)
        lines = result.split("\n")
        assert len(lines) == 3

    def test_indented(self):
        node = _ifelse([_branch(_bool(True), [_str("yes")])])
        result = _fmt().format_node(node, 1)
        assert result.startswith("  if")


# ── For Loop ─────────────────────────────────────────────────────────


class TestForLoop:
    def test_simple(self):
        node = _forloop("x", _id("items"), [_call("print", _id("x"))])
        result = _fmt().format_node(node, 0)
        assert result == "for x in items\n  print(x)"

    def test_function_call_iterable(self):
        node = _forloop("i", _call("range", _num(10)), [_call("print", _id("i"))])
        result = _fmt().format_node(node, 0)
        assert result == "for i in range(10)\n  print(i)"

    def test_multi_statement_body(self):
        body = [_bind("y", _binop(_id("x"), "*", _num(2))), _call("print", _id("y"))]
        node = _forloop("x", _id("items"), body)
        result = _fmt().format_node(node, 0)
        lines = result.split("\n")
        assert len(lines) == 3

    def test_nested_for(self):
        inner = _forloop("j", _id("cols"), [_call("draw", _id("i"), _id("j"))])
        node = _forloop("i", _id("rows"), [inner])
        result = _fmt().format_node(node, 0)
        assert "for i in rows" in result
        assert "  for j in cols" in result
        assert "    draw(i, j)" in result

    def test_indented(self):
        node = _forloop("x", _id("items"), [_id("x")])
        result = _fmt().format_node(node, 1)
        assert result.startswith("  for")


# ── Config Variations ────────────────────────────────────────────────


class TestConfigIndent:
    def test_indent_2(self):
        func = _funcdef(["x"], [_id("x")])
        result = _fmt(FmtConfig(indent_size=2)).format_node(_bind("f", func), 0)
        assert "\n  x" in result

    def test_indent_4(self):
        func = _funcdef(["x"], [_id("x")])
        result = _fmt(FmtConfig(indent_size=4)).format_node(_bind("f", func), 0)
        assert "\n    x" in result

    def test_indent_8(self):
        func = _funcdef(["x"], [_id("x")])
        result = _fmt(FmtConfig(indent_size=8)).format_node(_bind("f", func), 0)
        assert "\n        x" in result


class TestConfigBlankLines:
    def test_blank_lines_enabled(self):
        prog = _program(_bind("x", _num(1)), _bind("f", _funcdef(["a"], [_id("a")])))
        result = _fmt().format_program(prog)
        assert "\n\n" in result

    def test_blank_lines_disabled(self):
        cfg = FmtConfig(blank_lines_around_blocks=False)
        prog = _program(_bind("x", _num(1)), _bind("f", _funcdef(["a"], [_id("a")])))
        result = _fmt(cfg).format_program(prog)
        assert "\n\n" not in result


class TestConfigTrailingNewline:
    def test_trailing_newline_enabled(self):
        result = _fmt().format_program(_program(_bind("x", _num(1))))
        assert result.endswith("\n")

    def test_trailing_newline_disabled(self):
        cfg = FmtConfig(trailing_newline=False)
        result = _fmt(cfg).format_program(_program(_bind("x", _num(1))))
        assert not result.endswith("\n")


# ── format_program ───────────────────────────────────────────────────


class TestFormatProgram:
    def test_empty_program(self):
        assert _fmt().format_program(_program()) == ""

    def test_single_statement(self):
        result = _fmt().format_program(_program(_bind("x", _num(1))))
        assert result == "x := 1\n"

    def test_multiple_flat(self):
        prog = _program(_bind("x", _num(1)), _bind("y", _num(2)), _bind("z", _num(3)))
        result = _fmt().format_program(prog)
        assert result == "x := 1\ny := 2\nz := 3\n"

    def test_blank_line_before_function_def(self):
        prog = _program(_bind("x", _num(1)), _bind("f", _funcdef(["a"], [_id("a")])))
        result = _fmt().format_program(prog)
        lines = result.strip().split("\n")
        assert lines[1] == ""  # blank line

    def test_blank_line_before_if(self):
        prog = _program(_bind("x", _num(1)), _ifelse([_branch(_bool(True), [_id("x")])]))
        result = _fmt().format_program(prog)
        assert "\n\n" in result

    def test_blank_line_before_for(self):
        prog = _program(_bind("x", _num(1)), _forloop("i", _id("items"), [_id("i")]))
        result = _fmt().format_program(prog)
        assert "\n\n" in result

    def test_blank_line_after_block(self):
        prog = _program(
            _bind("f", _funcdef(["x"], [_id("x")])),
            _bind("y", _num(42)),
        )
        result = _fmt().format_program(prog)
        assert "\n\n" in result


# ── Complex Programs ─────────────────────────────────────────────────


class TestComplexPrograms:
    def test_fizzbuzz(self):
        body = [
            _ifelse(
                [
                    _branch(_binop(_binop(_id("i"), "%", _num(15)), "==", _num(0)), [_str("fizzbuzz")]),
                    _branch(_binop(_binop(_id("i"), "%", _num(3)), "==", _num(0)), [_str("fizz")]),
                    _branch(_binop(_binop(_id("i"), "%", _num(5)), "==", _num(0)), [_str("buzz")]),
                ],
            )
        ]
        func = _funcdef(["i"], body)
        prog = _program(_bind("fizzbuzz", func))
        result = _fmt().format_program(prog)
        assert "fizzbuzz := (i) =>" in result
        assert "if i % 15 == 0" in result
        assert "'fizzbuzz'" in result
        assert "elif i % 3 == 0" in result
        assert "elif i % 5 == 0" in result

    def test_nested_everything(self):
        prog = _program(
            _bind("max", _num(100)),
            _bind(
                "validate",
                _funcdef(
                    ["input"],
                    [
                        _ifelse(
                            [
                                _branch(_binop(_id("input"), ">", _num(0)), [_str("positive")]),
                                _branch(_binop(_id("input"), "<", _num(0)), [_str("negative")]),
                            ],
                            else_body=[_str("zero")],
                        )
                    ],
                ),
            ),
            _forloop("i", _call("range", _id("max")), [_call("validate", _id("i"))]),
        )
        result = _fmt().format_program(prog)
        assert "max := 100" in result
        assert "validate := (input) =>" in result
        assert "  if input > 0" in result
        assert "  elif input < 0" in result
        assert "  else" in result
        assert "for i in range(max)" in result
        assert "  validate(i)" in result
