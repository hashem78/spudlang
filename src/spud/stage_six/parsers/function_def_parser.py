from spud.stage_five.stage_five_token_type import StageFiveTokenType as T
from spud.stage_six.ast_node import ASTNode
from spud.stage_six.function_def import FunctionDef
from spud.stage_six.identifier import Identifier
from spud.stage_six.parse_error import ParseError
from spud.stage_six.parser_protocol import IParser
from spud.stage_six.token_stream import TokenStream


class FunctionDefParser:
    """Parse a function definition (anonymous function with fat arrow).

    Parses the grammar rule::

        function_def = '(' param_list ')' FAT_ARROW NEWLINE block
        param_list   = ( IDENTIFIER ( COMMA IDENTIFIER )* )?

    Function definitions in spud are always anonymous — they only
    get a name when bound via ``:=``. The ``BindingParser`` handles
    detecting whether a value is a function def and delegates here.

    The body is always an indented block (no single-expression
    inline bodies). The ``NEWLINE`` after ``=>`` and the
    ``INDENT``/``DEDENT`` around the body are consumed by this
    parser and the injected ``BlockParser`` respectively.

    Examples::

        (x) =>              → FunctionDef([x], [body...])
          x + 1

        (a, b) =>           → FunctionDef([a, b], [body...])
          result := a + b
          result

        () =>               → FunctionDef([], [body...])
          42
    """

    def __init__(self, block_parser: IParser[list[ASTNode]]):
        self._block_parser = block_parser

    def parse(self, stream: TokenStream) -> FunctionDef | ParseError:
        """Consume ``( params ) => NEWLINE`` and parse the body block."""
        paren_tok = stream.expect(T.PAREN_LEFT)
        if isinstance(paren_tok, ParseError):
            return paren_tok
        params = self._parse_param_list(stream)
        if isinstance(params, ParseError):
            return params
        rparen = stream.expect(T.PAREN_RIGHT)
        if isinstance(rparen, ParseError):
            return rparen
        arrow = stream.expect(T.FAT_ARROW)
        if isinstance(arrow, ParseError):
            return arrow
        nl = stream.expect(T.NEW_LINE)
        if isinstance(nl, ParseError):
            return nl
        body = self._block_parser.parse(stream)
        if isinstance(body, ParseError):
            return body
        end = body[-1].end if body else arrow.position
        return FunctionDef(position=paren_tok.position, end=end, params=params, body=body)

    def _parse_param_list(self, stream: TokenStream) -> list[Identifier] | ParseError:
        """Parse a comma-separated list of parameter identifiers.

        An empty list is valid — ``()`` means no parameters. Each
        parameter must be a bare identifier (no defaults, no type
        annotations, no destructuring).
        """
        params: list[Identifier] = []
        if stream.peek_type() == T.PAREN_RIGHT:
            return params
        first = stream.expect(T.IDENTIFIER)
        if isinstance(first, ParseError):
            return first
        params.append(Identifier(position=first.position, end=first.position, name=first.value))
        while stream.peek_type() == T.COMMA:
            stream.consume()
            param = stream.expect(T.IDENTIFIER)
            if isinstance(param, ParseError):
                return param
            params.append(Identifier(position=param.position, end=param.position, name=param.value))
        return params
