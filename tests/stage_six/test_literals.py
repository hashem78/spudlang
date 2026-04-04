from spud.stage_six import BooleanLiteral, Identifier, IntLiteral, Program, RawStringLiteral, StringLiteral
from tests.stage_six.helpers import parse


class TestEmptyInput:
    def test_empty_string(self):
        result = parse("")
        assert isinstance(result, Program)
        assert result.body == []

    def test_only_newlines(self):
        result = parse("\n\n\n")
        assert isinstance(result, Program)
        assert result.body == []


class TestLiterals:
    def test_numeric(self):
        result = parse("42")
        assert isinstance(result, Program)
        assert len(result.body) == 1
        node = result.body[0]
        assert isinstance(node, IntLiteral)
        assert node.value == 42

    def test_zero(self):
        result = parse("0")
        assert isinstance(result, Program)
        assert len(result.body) == 1
        node = result.body[0]
        assert isinstance(node, IntLiteral)
        assert node.value == 0

    def test_string(self):
        result = parse('"hello"')
        assert isinstance(result, Program)
        assert len(result.body) == 1
        node = result.body[0]
        assert isinstance(node, StringLiteral)
        assert node.value == "hello"

    def test_raw_string(self):
        result = parse("`raw`")
        assert isinstance(result, Program)
        assert len(result.body) == 1
        node = result.body[0]
        assert isinstance(node, RawStringLiteral)
        assert node.value == "raw"

    def test_boolean_true(self):
        result = parse("true")
        assert isinstance(result, Program)
        assert len(result.body) == 1
        node = result.body[0]
        assert isinstance(node, BooleanLiteral)
        assert node.value is True

    def test_boolean_false(self):
        result = parse("false")
        assert isinstance(result, Program)
        assert len(result.body) == 1
        node = result.body[0]
        assert isinstance(node, BooleanLiteral)
        assert node.value is False


class TestIdentifiers:
    def test_bare_identifier(self):
        result = parse("x")
        assert isinstance(result, Program)
        assert len(result.body) == 1
        node = result.body[0]
        assert isinstance(node, Identifier)
        assert node.name == "x"

    def test_multi_char_identifier(self):
        result = parse("foo")
        assert isinstance(result, Program)
        assert len(result.body) == 1
        node = result.body[0]
        assert isinstance(node, Identifier)
        assert node.name == "foo"
