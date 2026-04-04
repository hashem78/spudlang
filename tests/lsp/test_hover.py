from spud.core.pipeline import Pipeline
from spud.core.string_reader import StringReader
from spud.di.container import Container
from spud_check.type_checker import TypeChecker
from spud_check.typed_nodes.typed_program import TypedProgram
from spud_lsp.hover import HoverHandler

_CONTAINER = Container()
PIPELINE: Pipeline = _CONTAINER.pipeline()
CHECKER = TypeChecker()


def _typed_program(text: str) -> TypedProgram:
    result = PIPELINE.run(StringReader(text))
    check_result = CHECKER.check(result.program)
    tp = check_result.typed_program
    assert isinstance(tp, TypedProgram)
    return tp


class TestIntLiteralHover:
    def test_hover_on_int_literal(self):
        tp = _typed_program("x : Int := 42")
        handler = HoverHandler()
        result = handler.hover(tp, 0, 11)
        assert result is not None
        assert "Int" in result.contents.value


class TestIdentifierHover:
    def test_hover_on_identifier(self):
        tp = _typed_program("x : Int := 5\ny : Int := x")
        handler = HoverHandler()
        result = handler.hover(tp, 1, 11)
        assert result is not None
        assert "Int" in result.contents.value
        assert "x" in result.contents.value


class TestFunctionCallHover:
    def test_hover_on_function_call(self):
        text = "f : Function[[Int], Int] := (x : Int) : Int =>\n  x + 1\nf(1)"
        tp = _typed_program(text)
        handler = HoverHandler()
        result = handler.hover(tp, 2, 0)
        assert result is not None
        assert "Int" in result.contents.value


class TestOutOfRange:
    def test_returns_none(self):
        tp = _typed_program("x : Int := 5")
        handler = HoverHandler()
        result = handler.hover(tp, 100, 0)
        assert result is None
