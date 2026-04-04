from spud.stage_five.stage_five_token_type import StageFiveTokenType as T
from spud.stage_six.ast_node import ASTNode
from spud.stage_six.binding import Binding
from spud.stage_six.function_def import FunctionDef
from spud.stage_six.identifier import Identifier
from spud.stage_six.parse_error import ParseContextKind, ParseError, ctx, with_context
from spud.stage_six.parser_protocol import IParser
from spud.stage_six.parsers.type_parser import parse_type
from spud.stage_six.token_stream import TokenStream


class BindingParser:
    """Parse an immutable binding with a type annotation.

    Parses the grammar rule::

        binding = IDENTIFIER ':' type ':=' ( function_def | expression )

    Spud bindings are immutable — once a name is bound it cannot be
    reassigned. Every binding requires an explicit type annotation
    between the name and ``:=``. The value on the right side is
    either a function definition or a general expression.

    Function definitions are detected by lookahead: if the token
    after ``:=`` is ``(`` and scanning forward reveals a matching
    ``)`` followed by ``:`` (return type) then ``=>``, the value is
    parsed as a function definition. Otherwise it's parsed as a
    normal expression.

    Examples::

        x : Int := 5
        name : String := "spud"
        add : Function[[Int, Int], Int] := (a : Int, b : Int) : Int =>
          a + b
    """

    def __init__(self, expression_parser: IParser[ASTNode], function_def_parser: IParser[FunctionDef]):
        self._expression_parser = expression_parser
        self._function_def_parser = function_def_parser

    def parse(self, stream: TokenStream) -> Binding | ParseError:
        """Consume ``IDENTIFIER : type :=`` and parse the bound value."""
        target_tok = stream.expect(T.IDENTIFIER, context=ctx(ParseContextKind.BINDING_TARGET))
        if isinstance(target_tok, ParseError):
            return target_tok

        colon = stream.expect(T.COLON, context=ctx(ParseContextKind.TYPE_ANNOTATION))
        if isinstance(colon, ParseError):
            return colon

        type_ann = parse_type(stream)
        if isinstance(type_ann, ParseError):
            return type_ann

        walrus = stream.expect(T.WALRUS, context=ctx(ParseContextKind.BINDING_TARGET))
        if isinstance(walrus, ParseError):
            return walrus

        target = Identifier(position=target_tok.position, end=target_tok.position, name=target_tok.value)

        # Decide whether the value is a function definition or a
        # general expression. A function def starts with ``(`` and
        # has ``:`` (return type) then ``=>`` after the matching ``)``.
        # The lookahead scan is bounded by the parameter list length.
        if stream.peek_type() == T.PAREN_LEFT and self._is_function_def(stream):
            value = self._function_def_parser.parse(stream)
        else:
            value = self._expression_parser.parse(stream)

        if isinstance(value, ParseError):
            return with_context(value, ctx(ParseContextKind.BINDING_VALUE))
        return Binding(
            position=target_tok.position,
            end=value.end,
            target=target,
            type_annotation=type_ann,
            value=value,
        )

    def _is_function_def(self, stream: TokenStream) -> bool:
        """Scan ahead to check if tokens form a block function pattern.

        Walks forward from the current ``(`` without consuming,
        tracking parenthesis depth. When the matching ``)`` is found
        (depth returns to zero), checks whether the next token is
        ``:`` (return type annotation). Then scans past the return
        type to find ``=>`` followed by ``NEWLINE`` — indicating a
        block function definition.

        Inline functions (``(params) : Type => expr``) return False
        here so they fall through to the expression parser which
        handles them as ``InlineFunctionDef`` nodes.
        """
        depth = 0
        offset = 0
        while True:
            tok = stream.peek_at(offset)
            if tok is None:
                return False
            match tok.token_type:
                case T.PAREN_LEFT:
                    depth += 1
                case T.PAREN_RIGHT:
                    depth -= 1
                    if depth == 0:
                        colon = stream.peek_at(offset + 1)
                        if colon is None or colon.token_type != T.COLON:
                            return False
                        return self._scan_past_return_type(stream, offset + 2)
            offset += 1

    def _scan_past_return_type(self, stream: TokenStream, offset: int) -> bool:
        """Skip past a return type to find ``=> NEWLINE``.

        The return type may contain nested brackets (e.g.
        ``List[Int]`` or ``Function[[Int], Int]``), so bracket
        depth is tracked.
        """
        depth = 0
        while True:
            tok = stream.peek_at(offset)
            if tok is None:
                return False
            match tok.token_type:
                case T.BRACKET_LEFT:
                    depth += 1
                case T.BRACKET_RIGHT:
                    depth -= 1
                case T.FAT_ARROW if depth == 0:
                    newline = stream.peek_at(offset + 1)
                    return newline is not None and newline.token_type == T.NEW_LINE
            offset += 1
