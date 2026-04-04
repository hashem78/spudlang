from spud.stage_five import StageFiveTokenType as T
from spud.stage_six import ASTNode, Binding, ForLoop, IfElse, IParser, TokenStream
from spud.stage_six.parse_errors import ParseContextKind, ParseError, UnexpectedTokenError, ctx


class StatementParser:
    """Dispatch parser that routes to the correct statement parser.

    Parses the grammar rule::

        statement = binding | if_else | for_loop | expression

    Disambiguation is done by peeking at the current (and sometimes
    next) token:

    - ``IF``             → delegate to ``IfElseParser``
    - ``FOR``            → delegate to ``ForLoopParser``
    - ``IDENTIFIER :``   → delegate to ``BindingParser``
      (two-token lookahead: current is IDENTIFIER, next is COLON)
    - anything else      → delegate to ``ExpressionParser``
      (bare expressions like function calls or literals)

    This parser never consumes tokens itself — it only peeks to
    decide which sub-parser to invoke, then hands off completely.
    """

    def __init__(
        self,
        expression_parser: IParser[ASTNode],
        binding_parser: IParser[Binding],
        if_else_parser: IParser[IfElse],
        for_loop_parser: IParser[ForLoop],
    ):
        self._expression_parser = expression_parser
        self._binding_parser = binding_parser
        self._if_else_parser = if_else_parser
        self._for_loop_parser = for_loop_parser

    def parse(self, stream: TokenStream) -> ASTNode | ParseError:
        """Peek at the stream and delegate to the appropriate parser."""
        match stream.peek_type():
            case T.IF:
                return self._if_else_parser.parse(stream)
            case T.FOR:
                return self._for_loop_parser.parse(stream)
            case T.IDENTIFIER if self._peek_type_at(stream, 1) == T.COLON:
                return self._binding_parser.parse(stream)
            case T.ELSE:
                tok = stream.consume()
                return UnexpectedTokenError(
                    position=tok.position,
                    got=T.ELSE,
                    context=ctx(ParseContextKind.ORPHANED_ELSE),
                )
            case T.ELIF:
                tok = stream.consume()
                return UnexpectedTokenError(
                    position=tok.position,
                    got=T.ELIF,
                    context=ctx(ParseContextKind.ORPHANED_ELIF),
                )
            case _:
                return self._expression_parser.parse(stream)

    def _peek_type_at(self, stream: TokenStream, offset: int) -> T | None:
        tok = stream.peek_at(offset)
        return tok.token_type if tok else None
