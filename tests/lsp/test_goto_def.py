from spud.core import StringReader
from spud.core.pipeline import Pipeline
from spud.di import Container
from spud.stage_six import Program
from spud_lsp import GotoDefHandler

_CONTAINER = Container()
PIPELINE: Pipeline = _CONTAINER.pipeline()
URI = "file:///test.spud"


def _program(text: str) -> Program:
    return PIPELINE.run(StringReader(text)).program


class TestTopLevelBinding:
    def test_goto_def_on_reference(self):
        program = _program("x : Int := 5\ny : Int := x + 1")
        handler = GotoDefHandler()
        result = handler.goto_def(program, URI, 1, 11)
        assert result is not None
        assert result.range.start.line == 0
        assert result.range.start.character == 0


class TestFunctionParam:
    def test_goto_def_on_param_in_body(self):
        program = _program("f : Function[[Int], Int] := (a : Int) : Int =>\n  a + 1")
        handler = GotoDefHandler()
        result = handler.goto_def(program, URI, 1, 2)
        assert result is not None
        assert result.range.start.line == 0
        assert result.range.start.character == 29


class TestSameNameParamsDifferentFunctions:
    def test_goto_def_resolves_to_correct_function(self):
        text = (
            "f : Function[[Int], Int] := (a : Int) : Int =>\n"
            "  a + 1\n"
            "g : Function[[Int], Int] := (a : Int) : Int =>\n"
            "  a + 2"
        )
        program = _program(text)
        handler = GotoDefHandler()
        result = handler.goto_def(program, URI, 3, 2)
        assert result is not None
        assert result.range.start.line == 2
        assert result.range.start.character == 29


class TestForLoopVariable:
    def test_goto_def_on_loop_variable(self):
        text = "xs : List[Int] := [1]\nfor i : Int in xs\n  y : Int := i"
        program = _program(text)
        handler = GotoDefHandler()
        result = handler.goto_def(program, URI, 2, 13)
        assert result is not None
        assert result.range.start.line == 1
        assert result.range.start.character == 4


class TestFunctionCallCallee:
    def test_goto_def_on_callee(self):
        text = "f : Function[[Int], Int] := (x : Int) : Int =>\n  x + 1\nf(1)"
        program = _program(text)
        handler = GotoDefHandler()
        result = handler.goto_def(program, URI, 2, 0)
        assert result is not None
        assert result.range.start.line == 0
        assert result.range.start.character == 0


class TestOutOfRange:
    def test_returns_none(self):
        program = _program("x : Int := 5")
        handler = GotoDefHandler()
        result = handler.goto_def(program, URI, 100, 0)
        assert result is None
