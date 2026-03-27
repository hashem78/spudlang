from spud.core.position import Position
from spud.stage_five.stage_five_token_type import StageFiveTokenType as T
from spud.stage_six.ast_node import ASTNode
from spud.stage_six.parse_error import ParseError
from spud.stage_six.parser_protocol import IParser
from spud.stage_six.program import Program
from spud.stage_six.token_stream import TokenStream


class ProgramParser:
    """Top-level parser that produces the root ``Program`` AST node.

    Parses the grammar rule::

        program = NEWLINE* ( statement NEWLINE* )* EOF

    Consumes the entire token stream, delegating each statement to
    the injected ``StatementParser``. Newlines between statements
    (including leading and trailing) are silently skipped — they
    serve as expression boundaries in the stream but carry no
    semantic meaning at the program level.

    Returns ``Program(body=[...])`` on success, or the first
    ``ParseError`` encountered by any sub-parser.
    """

    def __init__(self, statement_parser: IParser[ASTNode]):
        self._statement_parser = statement_parser

    def parse(self, stream: TokenStream) -> Program | ParseError:
        """Parse the full token stream into a Program."""
        body: list[ASTNode] = []
        self._skip_newlines(stream)
        while not stream.at_end():
            stmt = self._statement_parser.parse(stream)
            if isinstance(stmt, ParseError):
                return stmt
            body.append(stmt)
            self._skip_newlines(stream)
        return Program(position=Position(line=0, column=0), body=body)

    def _skip_newlines(self, stream: TokenStream) -> None:
        while stream.peek_type() == T.NEW_LINE:
            stream.consume()
