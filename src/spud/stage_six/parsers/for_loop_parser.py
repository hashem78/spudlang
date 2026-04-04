from spud.stage_five import StageFiveTokenType as T
from spud.stage_six import ASTNode, ForLoop, Identifier, IParser, TokenStream
from spud.stage_six.parse_errors import ParseContextKind, ParseError, ctx, with_context
from spud.stage_six.parsers.type_parser import parse_type


class ForLoopParser:
    """Parse a for loop with a typed loop variable.

    Parses the grammar rule::

        for_loop = FOR IDENTIFIER ':' type IN expression NEWLINE block

    The loop variable is always a bare identifier with a type
    annotation. The iterable is a full expression (can be a
    function call like ``range(n)``, an identifier, or any other
    expression). The body is an indented block.

    Examples::

        for i : Int in items
          process(i)

        for x : Int in range(10)
          compute(x)
    """

    def __init__(self, expression_parser: IParser[ASTNode], block_parser: IParser[list[ASTNode]]):
        self._expression_parser = expression_parser
        self._block_parser = block_parser

    def parse(self, stream: TokenStream) -> ForLoop | ParseError:
        """Consume ``for IDENTIFIER : type in expression NEWLINE`` and parse the body."""
        for_tok = stream.expect(T.FOR, context=ctx(ParseContextKind.FOR_VARIABLE))
        if isinstance(for_tok, ParseError):
            return for_tok
        var_tok = stream.expect(T.IDENTIFIER, context=ctx(ParseContextKind.FOR_VARIABLE))
        if isinstance(var_tok, ParseError):
            return var_tok
        colon = stream.expect(T.COLON, context=ctx(ParseContextKind.TYPE_ANNOTATION))
        if isinstance(colon, ParseError):
            return colon
        var_type = parse_type(stream)
        if isinstance(var_type, ParseError):
            return var_type
        in_tok = stream.expect(T.IN, context=ctx(ParseContextKind.FOR_VARIABLE))
        if isinstance(in_tok, ParseError):
            return in_tok

        iterable = self._expression_parser.parse(stream)
        if isinstance(iterable, ParseError):
            return with_context(iterable, ctx(ParseContextKind.FOR_ITERABLE))

        nl = stream.expect(T.NEW_LINE, context=ctx(ParseContextKind.FOR_BODY))
        if isinstance(nl, ParseError):
            return nl
        body = self._block_parser.parse(stream)
        if isinstance(body, ParseError):
            return with_context(body, ctx(ParseContextKind.FOR_BODY))

        return ForLoop(
            position=for_tok.position,
            end=body[-1].end if body else iterable.end,
            variable=Identifier(position=var_tok.position, end=var_tok.position, name=var_tok.value),
            variable_type=var_type,
            iterable=iterable,
            body=body,
        )
