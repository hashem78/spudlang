from spud.stage_five.stage_five_token_type import StageFiveTokenType as T
from spud.stage_six.ast_node import ASTNode
from spud.stage_six.condition_branch import ConditionBranch
from spud.stage_six.if_else import IfElse
from spud.stage_six.parse_error import ParseError
from spud.stage_six.parser_protocol import IParser
from spud.stage_six.token_stream import TokenStream


class IfElseParser:
    """Parse an if/elif/else chain into a single ``IfElse`` AST node.

    Parses the grammar rule::

        if_else = IF expression NEWLINE block
                  ( ELIF expression NEWLINE block )*
                  ( ELSE NEWLINE block )?

    Rather than producing separate AST nodes for each branch, this
    parser collapses the entire chain into one ``IfElse`` node with
    a list of ``ConditionBranch`` entries and an optional else body.
    This means the interpreter doesn't need to reconstruct sibling
    relationships — the grouping is done at parse time.

    After parsing an ``if`` block, the parser peeks for ``ELIF`` and
    ``ELSE`` tokens at the same indentation level. These appear as
    the next tokens in the stream after the preceding block's
    ``DEDENT`` has been consumed.

    Examples::

        if x > 0            → IfElse(
          "positive"             branches=[Branch(x > 0, ["positive"])],
                                 else_body=None)

        if x > 0            → IfElse(
          "positive"             branches=[
        elif x == 0                Branch(x > 0, ["positive"]),
          "zero"                   Branch(x == 0, ["zero"])],
        else                     else_body=["negative"])
          "negative"
    """

    def __init__(self, expression_parser: IParser[ASTNode], block_parser: IParser[list[ASTNode]]):
        self._expression_parser = expression_parser
        self._block_parser = block_parser

    def parse(self, stream: TokenStream) -> IfElse | ParseError:
        """Consume the ``if`` keyword and collect all branches."""
        if_tok = stream.expect(T.IF)
        if isinstance(if_tok, ParseError):
            return if_tok
        branches: list[ConditionBranch] = []

        # First branch: ``if condition NEWLINE block``.
        condition = self._expression_parser.parse(stream)
        if isinstance(condition, ParseError):
            return condition
        nl = stream.expect(T.NEW_LINE)
        if isinstance(nl, ParseError):
            return nl
        body = self._block_parser.parse(stream)
        if isinstance(body, ParseError):
            return body
        branch_end = body[-1].end if body else condition.end
        branches.append(ConditionBranch(position=if_tok.position, end=branch_end, condition=condition, body=body))

        # Elif branches: zero or more ``elif condition NEWLINE block``.
        while stream.peek_type() == T.ELIF:
            elif_tok = stream.expect(T.ELIF)
            if isinstance(elif_tok, ParseError):
                return elif_tok
            condition = self._expression_parser.parse(stream)
            if isinstance(condition, ParseError):
                return condition
            nl = stream.expect(T.NEW_LINE)
            if isinstance(nl, ParseError):
                return nl
            body = self._block_parser.parse(stream)
            if isinstance(body, ParseError):
                return body
            branch_end = body[-1].end if body else condition.end
            branches.append(ConditionBranch(position=elif_tok.position, end=branch_end, condition=condition, body=body))

        # Else branch: optional ``else NEWLINE block``.
        else_body = None
        if stream.peek_type() == T.ELSE:
            else_tok = stream.expect(T.ELSE)
            if isinstance(else_tok, ParseError):
                return else_tok
            nl = stream.expect(T.NEW_LINE)
            if isinstance(nl, ParseError):
                return nl
            else_body_result = self._block_parser.parse(stream)
            if isinstance(else_body_result, ParseError):
                return else_body_result
            else_body = else_body_result

        if else_body:
            end = else_body[-1].end
        else:
            end = branches[-1].end
        return IfElse(position=if_tok.position, end=end, branches=branches, else_body=else_body)
