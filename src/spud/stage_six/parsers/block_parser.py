from spud.stage_five import StageFiveTokenType as T
from spud.stage_six import ASTNode, IParser, TokenStream
from spud.stage_six.parse_errors import ParseError


class BlockParser:
    """Parse an indented block of statements.

    Parses the grammar rule::

        block = INDENT NEWLINE* ( statement NEWLINE* )* DEDENT

    Blocks appear as the body of control flow constructs (if/else,
    for) and function definitions. Stage five emits INDENT when
    indentation increases and DEDENT when it decreases, so a block
    is always bracketed by exactly one INDENT/DEDENT pair.

    Newlines within the block are skipped — they separate statements
    but don't produce AST nodes. An empty block (INDENT immediately
    followed by DEDENT) is valid and returns an empty list.

    This parser has a circular dependency with ``StatementParser``:
    blocks contain statements, and statements (like if/else) contain
    blocks. This is resolved at DI wiring time by constructing the
    ``BlockParser`` before its ``StatementParser`` dependency is
    fully initialized.
    """

    def __init__(self, statement_parser: IParser[ASTNode]):
        self._statement_parser = statement_parser

    def parse(self, stream: TokenStream) -> list[ASTNode] | ParseError:
        """Consume INDENT, parse statements until DEDENT, return body list."""
        result = stream.expect(T.INDENT)
        if isinstance(result, ParseError):
            return result
        body: list[ASTNode] = []
        self._skip_newlines(stream)
        while stream.peek_type() not in (T.DEDENT, None):
            stmt = self._statement_parser.parse(stream)
            if isinstance(stmt, ParseError):
                return stmt
            body.append(stmt)
            self._skip_newlines(stream)
        result = stream.expect(T.DEDENT)
        if isinstance(result, ParseError):
            return result
        return body

    def _skip_newlines(self, stream: TokenStream) -> None:
        while stream.peek_type() == T.NEW_LINE:
            stream.consume()
