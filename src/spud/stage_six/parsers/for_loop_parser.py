from spud.stage_five.stage_five_token_type import StageFiveTokenType as T
from spud.stage_six.ast_node import ASTNode
from spud.stage_six.for_loop import ForLoop
from spud.stage_six.identifier import Identifier
from spud.stage_six.parse_error import ParseError
from spud.stage_six.parser_protocol import IParser
from spud.stage_six.token_stream import TokenStream


class ForLoopParser:
    """Parse a for loop.

    Parses the grammar rule::

        for_loop = FOR IDENTIFIER IN expression NEWLINE block

    The loop variable is always a bare identifier — no destructuring
    or pattern matching. The iterable is a full expression (can be a
    function call like ``range(n)``, an identifier, or any other
    expression). The body is an indented block.

    Examples::

        for i in items       → ForLoop(i, Identifier(items), [body...])
          process(i)

        for x in range(10)   → ForLoop(x, FunctionCall(range, [10]), [body...])
          compute(x)
    """

    def __init__(self, expression_parser: IParser[ASTNode], block_parser: IParser[list[ASTNode]]):
        self._expression_parser = expression_parser
        self._block_parser = block_parser

    def parse(self, stream: TokenStream) -> ForLoop | ParseError:
        """Consume ``for IDENTIFIER in expression NEWLINE`` and parse the body."""
        for_tok = stream.expect(T.FOR)
        if isinstance(for_tok, ParseError):
            return for_tok
        var_tok = stream.expect(T.IDENTIFIER)
        if isinstance(var_tok, ParseError):
            return var_tok
        in_tok = stream.expect(T.IN)
        if isinstance(in_tok, ParseError):
            return in_tok

        iterable = self._expression_parser.parse(stream)
        if isinstance(iterable, ParseError):
            return iterable

        nl = stream.expect(T.NEW_LINE)
        if isinstance(nl, ParseError):
            return nl
        body = self._block_parser.parse(stream)
        if isinstance(body, ParseError):
            return body

        return ForLoop(
            position=for_tok.position,
            variable=Identifier(position=var_tok.position, name=var_tok.value),
            iterable=iterable,
            body=body,
        )
