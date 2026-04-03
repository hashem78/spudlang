from spud_fmt.config import FmtConfig, QuoteStyle
from tests.fmt.helpers import bind, bool_, call, fmt, id, inline_funcdef, list_, num, raw, str_


class TestIdentifier:
    def test_simple(self):
        assert fmt().format_node(id("x"), 0) == "x"

    def test_underscore(self):
        assert fmt().format_node(id("my_var"), 0) == "my_var"

    def test_single_char(self):
        assert fmt().format_node(id("a"), 0) == "a"


class TestNumeric:
    def test_zero(self):
        assert fmt().format_node(num(0), 0) == "0"

    def test_one(self):
        assert fmt().format_node(num(1), 0) == "1"

    def test_large(self):
        assert fmt().format_node(num(999999), 0) == "999999"


class TestString:
    def test_simple_single_quotes(self):
        assert fmt().format_node(str_("hello"), 0) == "'hello'"

    def test_simple_double_quotes(self):
        cfg = FmtConfig(quote_style=QuoteStyle.DOUBLE)
        assert fmt(cfg).format_node(str_("hello"), 0) == '"hello"'

    def test_escape_single_quote(self):
        assert fmt().format_node(str_("it's"), 0) == "'it\\'s'"

    def test_escape_double_quote(self):
        cfg = FmtConfig(quote_style=QuoteStyle.DOUBLE)
        assert fmt(cfg).format_node(str_('say "hi"'), 0) == '"say \\"hi\\""'

    def test_escape_backslash(self):
        assert fmt().format_node(str_("a\\b"), 0) == "'a\\\\b'"

    def test_empty(self):
        assert fmt().format_node(str_(""), 0) == "''"


class TestRawString:
    def test_simple(self):
        assert fmt().format_node(raw("hello"), 0) == "`hello`"

    def test_with_quotes(self):
        assert fmt().format_node(raw('say "hi"'), 0) == '`say "hi"`'

    def test_with_newline(self):
        assert fmt().format_node(raw("a\nb"), 0) == "`a\nb`"

    def test_empty(self):
        assert fmt().format_node(raw(""), 0) == "``"


class TestBoolean:
    def test_true(self):
        assert fmt().format_node(bool_(True), 0) == "true"

    def test_false(self):
        assert fmt().format_node(bool_(False), 0) == "false"


class TestListLiteral:
    def test_empty(self):
        assert fmt().format_node(list_(), 0) == "[]"

    def test_single_element(self):
        assert fmt().format_node(list_(num(1)), 0) == "[1]"

    def test_multiple_elements(self):
        assert fmt().format_node(list_(num(1), num(2), num(3)), 0) == "[1, 2, 3]"

    def test_no_comma_space(self):
        cfg = FmtConfig(space_after_comma=False)
        assert fmt(cfg).format_node(list_(num(1), num(2)), 0) == "[1,2]"

    def test_nested_lists(self):
        assert fmt().format_node(list_(list_(num(1)), list_(num(2))), 0) == "[[1], [2]]"

    def test_mixed_expressions(self):
        node = list_(num(1), call("max", num(1), num(2)), inline_funcdef(["a", "b"], num(33)))
        assert fmt().format_node(node, 0) == "[1, max(1, 2), (a, b) => 33]"

    def test_in_binding(self):
        assert fmt().format_node(bind("x", list_(num(1), num(2))), 0) == "x := [1, 2]"
