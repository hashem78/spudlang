from spud_fmt import FmtConfig
from tests.fmt.helpers import binop, call, fmt, id, neg, num, pos


class TestBinaryOp:
    def test_simple(self):
        assert fmt().format_node(binop(id("a"), "+", id("b")), 0) == "a + b"

    def test_no_spaces(self):
        cfg = FmtConfig(spaces_around_operators=False)
        assert fmt(cfg).format_node(binop(id("a"), "+", id("b")), 0) == "a+b"

    def test_chained_same_precedence(self):
        node = binop(id("a"), "+", binop(id("b"), "+", id("c")))
        assert fmt().format_node(node, 0) == "a + b + c"

    def test_higher_precedence_no_parens(self):
        node = binop(id("a"), "+", binop(id("b"), "*", id("c")))
        assert fmt().format_node(node, 0) == "a + b * c"

    def test_lower_precedence_needs_parens(self):
        node = binop(binop(id("a"), "+", id("b")), "*", id("c"))
        assert fmt().format_node(node, 0) == "(a + b) * c"

    def test_non_commutative_right_child_gets_parens(self):
        node = binop(id("a"), "*", binop(num(1), "/", num(2)))
        assert fmt().format_node(node, 0) == "a * (1 / 2)"

    def test_non_commutative_parent_right_gets_parens(self):
        node = binop(num(6), "/", binop(num(2), "*", num(3)))
        assert fmt().format_node(node, 0) == "6 / (2 * 3)"

    def test_subtract_grouped_add(self):
        node = binop(id("a"), "-", binop(id("b"), "+", id("c")))
        assert fmt().format_node(node, 0) == "a - (b + c)"

    def test_commutative_same_prec_no_parens(self):
        node = binop(id("a"), "+", binop(id("b"), "+", id("c")))
        assert fmt().format_node(node, 0) == "a + b + c"

    def test_comparison(self):
        assert fmt().format_node(binop(id("x"), "==", num(5)), 0) == "x == 5"

    def test_logical_and(self):
        assert fmt().format_node(binop(id("a"), "&&", id("b")), 0) == "a && b"

    def test_logical_or(self):
        assert fmt().format_node(binop(id("a"), "||", id("b")), 0) == "a || b"

    def test_modulo(self):
        assert fmt().format_node(binop(id("i"), "%", num(15)), 0) == "i % 15"

    def test_mixed_precedence(self):
        inner = binop(id("b"), "*", id("c"))
        left = binop(id("a"), "+", inner)
        node = binop(left, "-", id("d"))
        result = fmt().format_node(node, 0)
        assert "a + b * c" in result

    def test_all_operators(self):
        for op in ["+", "-", "*", "/", "%", "==", "!=", "<", ">", "<=", ">=", "&&", "||"]:
            result = fmt().format_node(binop(id("a"), op, id("b")), 0)
            assert f"a {op} b" == result


class TestUnaryOp:
    def test_negative_number(self):
        assert fmt().format_node(neg(num(5)), 0) == "-5"

    def test_negative_identifier(self):
        assert fmt().format_node(neg(id("x")), 0) == "-x"

    def test_double_negation_collapses(self):
        assert fmt().format_node(neg(neg(id("x"))), 0) == "x"

    def test_triple_negation_collapses(self):
        assert fmt().format_node(neg(neg(neg(id("x")))), 0) == "-x"

    def test_quad_negation_collapses(self):
        assert fmt().format_node(neg(neg(neg(neg(id("x"))))), 0) == "x"

    def test_negative_expression(self):
        assert fmt().format_node(neg(binop(id("a"), "+", id("b"))), 0) == "-(a + b)"

    def test_negative_function_call(self):
        assert fmt().format_node(neg(call("foo", num(1))), 0) == "-foo(1)"

    def test_binding_to_negative(self):
        from tests.fmt.helpers import bind

        assert fmt().format_node(bind("x", neg(num(5))), 0) == "x: Int := -5"

    def test_unary_plus(self):
        assert fmt().format_node(pos(num(5)), 0) == "+5"

    def test_unary_plus_collapses_to_one(self):
        assert fmt().format_node(pos(pos(id("x"))), 0) == "+x"

    def test_unary_plus_triple(self):
        assert fmt().format_node(pos(pos(pos(id("x")))), 0) == "+x"

    def test_plus_minus(self):
        assert fmt().format_node(pos(neg(id("x"))), 0) == "-x"

    def test_minus_plus(self):
        assert fmt().format_node(neg(pos(id("x"))), 0) == "-x"

    def test_plus_plus_minus(self):
        assert fmt().format_node(pos(pos(neg(id("x")))), 0) == "-x"

    def test_minus_minus_plus(self):
        assert fmt().format_node(neg(neg(pos(id("x")))), 0) == "+x"

    def test_plus_minus_minus(self):
        assert fmt().format_node(pos(neg(neg(id("x")))), 0) == "+x"

    def test_collapse_unary_plus_config(self):
        cfg = FmtConfig(collapse_unary_plus=True)
        assert fmt(cfg).format_node(pos(num(5)), 0) == "5"

    def test_collapse_unary_plus_config_double(self):
        cfg = FmtConfig(collapse_unary_plus=True)
        assert fmt(cfg).format_node(pos(pos(id("x"))), 0) == "x"

    def test_collapse_unary_plus_neg_still_works(self):
        cfg = FmtConfig(collapse_unary_plus=True)
        assert fmt(cfg).format_node(neg(num(5)), 0) == "-5"

    def test_unary_plus_on_binary_op(self):
        assert fmt().format_node(pos(binop(id("a"), "+", id("b"))), 0) == "+(a + b)"
