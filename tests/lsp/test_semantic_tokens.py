from spud.core.pipeline import Pipeline
from spud.core.string_reader import StringReader
from spud.di.container import Container
from spud_lsp.semantic_tokens import TOKEN_TYPES, SemanticTokensHandler

_CONTAINER = Container()
PIPELINE: Pipeline = _CONTAINER.pipeline()


def _run(text: str) -> list[tuple[int, int, int, str, bool]]:
    result = PIPELINE.run(StringReader(text))
    handler = SemanticTokensHandler()
    st = handler.semantic_tokens(result.resolve_result, result.tokens)
    return _decode(st.data)


def _decode(data: list[int]) -> list[tuple[int, int, int, str, bool]]:
    result = []
    prev_line = 0
    prev_col = 0
    i = 0
    while i < len(data):
        dl, dc, length, tt, mods = data[i : i + 5]
        line = prev_line + dl
        col = (prev_col + dc) if dl == 0 else dc
        result.append((line, col, length, TOKEN_TYPES[tt], bool(mods & 1)))
        prev_line = line
        prev_col = col
        i += 5
    return result


class TestSimpleBinding:
    def test_variable_declaration(self):
        tokens = _run("x := 5")
        assert (0, 0, 1, "variable", True) in tokens

    def test_walrus_operator(self):
        tokens = _run("x := 5")
        assert (0, 2, 2, "operator", False) in tokens

    def test_number(self):
        tokens = _run("x := 5")
        assert (0, 5, 1, "number", False) in tokens


class TestMultiDigitNumber:
    def test_length(self):
        tokens = _run("x := 42")
        assert (0, 5, 2, "number", False) in tokens

    def test_large_number(self):
        tokens = _run("x := 12345")
        assert (0, 5, 5, "number", False) in tokens


class TestFloatLiteral:
    def test_float(self):
        tokens = _run("x := 3.14")
        assert (0, 5, 4, "number", False) in tokens

    def test_trailing_dot(self):
        tokens = _run("x := 3.")
        assert (0, 5, 3, "number", False) in tokens

    def test_leading_dot(self):
        tokens = _run("x := .5")
        assert (0, 5, 3, "number", False) in tokens


class TestStringLiteral:
    def test_single_quoted(self):
        tokens = _run("x := 'hello'")
        assert (0, 5, 7, "string", False) in tokens

    def test_double_quoted(self):
        tokens = _run('x := "hello"')
        assert (0, 5, 7, "string", False) in tokens

    def test_empty_string(self):
        tokens = _run("x := ''")
        assert (0, 5, 2, "string", False) in tokens


class TestFunctionBinding:
    def test_function_name_is_function_declaration(self):
        tokens = _run("f := (x) => x")
        assert (0, 0, 1, "function", True) in tokens

    def test_param_is_parameter_declaration(self):
        tokens = _run("f := (x) => x")
        assert (0, 6, 1, "parameter", True) in tokens

    def test_param_reference_in_body(self):
        tokens = _run("f := (x) => x")
        assert (0, 12, 1, "parameter", False) in tokens


class TestFunctionCall:
    def test_callee_is_function(self):
        tokens = _run("f := (x) => x\nf(1)")
        func_refs = [(ln, c, le, t, d) for ln, c, le, t, d in tokens if ln == 1 and t == "function"]
        assert len(func_refs) == 1
        assert func_refs[0] == (1, 0, 1, "function", False)

    def test_arg_is_number(self):
        tokens = _run("f := (x) => x\nf(1)")
        assert (1, 2, 1, "number", False) in tokens


class TestKeywords:
    def test_if_keyword(self):
        tokens = _run("x := 1\nif true\n  x")
        assert (1, 0, 2, "keyword", False) in tokens

    def test_true_keyword(self):
        tokens = _run("x := 1\nif true\n  x")
        assert (1, 3, 4, "keyword", False) in tokens

    def test_else_keyword(self):
        tokens = _run("x := 1\nif true\n  x\nelse\n  x")
        assert (3, 0, 4, "keyword", False) in tokens

    def test_for_and_in_keywords(self):
        tokens = _run("x := [1]\nfor i in x\n  i")
        keywords = [(ln, c, le, t, d) for ln, c, le, t, d in tokens if t == "keyword"]
        keyword_texts = [(ln, c, le) for ln, c, le, _, _ in keywords]
        assert (1, 0, 3) in keyword_texts
        assert (1, 6, 2) in keyword_texts


class TestOperators:
    def test_arithmetic(self):
        tokens = _run("x := 1 + 2")
        assert (0, 7, 1, "operator", False) in tokens

    def test_comparison(self):
        tokens = _run("x := 1 == 2")
        assert (0, 7, 2, "operator", False) in tokens

    def test_logical(self):
        tokens = _run("x := true && false")
        assert (0, 10, 2, "operator", False) in tokens


class TestForLoop:
    def test_loop_variable_is_declaration(self):
        tokens = _run("x := [1]\nfor i in x\n  i")
        assert (1, 4, 1, "variable", True) in tokens

    def test_loop_variable_reference_in_body(self):
        tokens = _run("x := [1]\nfor i in x\n  i")
        assert (2, 2, 1, "variable", False) in tokens


class TestIdentifierClassification:
    def test_variable_reference(self):
        tokens = _run("x := 1\ny := x")
        assert (1, 5, 1, "variable", False) in tokens

    def test_function_reference(self):
        tokens = _run("f := (x) => x\ny := f")
        refs = [(ln, c, le, t, d) for ln, c, le, t, d in tokens if ln == 1 and c == 5]
        assert refs[0][3] == "function"

    def test_parameter_reference(self):
        tokens = _run("f := (x) => x")
        assert (0, 12, 1, "parameter", False) in tokens
