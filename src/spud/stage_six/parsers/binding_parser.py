from spud.stage_five.stage_five_token_type import StageFiveTokenType as T
from spud.stage_six.ast_node import ASTNode
from spud.stage_six.binding import Binding
from spud.stage_six.function_def import FunctionDef
from spud.stage_six.identifier import Identifier
from spud.stage_six.parse_error import ParseContextKind, ParseError, ctx, with_context
from spud.stage_six.parser_protocol import IParser
from spud.stage_six.token_stream import TokenStream


class BindingParser:
    """Parse an immutable binding (variable assignment).

    Parses the grammar rule::

        binding = IDENTIFIER WALRUS ( function_def | expression )

    Spud bindings are immutable — once a name is bound it cannot be
    reassigned. The value on the right side of ``:=`` is either a
    function definition or a general expression.

    Function definitions are detected by lookahead: if the token
    after ``:=`` is ``(`` and scanning forward reveals a matching
    ``)`` followed by ``=>``, the value is parsed as a function
    definition. Otherwise it's parsed as a normal expression.

    Examples::

        x := 5                      → Binding(x, NumericLiteral(5))
        name := "spud"              → Binding(name, StringLiteral("spud"))
        add := (a, b) =>            → Binding(add, FunctionDef([a, b], [...]))
          a + b
    """

    def __init__(self, expression_parser: IParser[ASTNode], function_def_parser: IParser[FunctionDef]):
        self._expression_parser = expression_parser
        self._function_def_parser = function_def_parser

    def parse(self, stream: TokenStream) -> Binding | ParseError:
        """Consume ``IDENTIFIER :=`` and parse the bound value."""
        target_tok = stream.expect(T.IDENTIFIER, context=ctx(ParseContextKind.BINDING_TARGET))
        if isinstance(target_tok, ParseError):
            return target_tok
        walrus = stream.expect(T.WALRUS, context=ctx(ParseContextKind.BINDING_TARGET))
        if isinstance(walrus, ParseError):
            return walrus
        target = Identifier(position=target_tok.position, end=target_tok.position, name=target_tok.value)

        # Decide whether the value is a function definition or a
        # general expression. A function def starts with ``(`` and
        # has ``=>`` after the matching ``)``. The lookahead scan
        # is bounded by the parameter list length.
        if stream.peek_type() == T.PAREN_LEFT and self._is_function_def(stream):
            value = self._function_def_parser.parse(stream)
        else:
            value = self._expression_parser.parse(stream)

        if isinstance(value, ParseError):
            return with_context(value, ctx(ParseContextKind.BINDING_VALUE))
        return Binding(position=target_tok.position, end=value.end, target=target, value=value)

    def _is_function_def(self, stream: TokenStream) -> bool:
        """Scan ahead to check if tokens form a ``(params) =>`` pattern.

        Walks forward from the current ``(`` without consuming,
        tracking parenthesis depth. When the matching ``)`` is found
        (depth returns to zero), checks whether the next token is
        ``=>``. Handles nested parentheses in the parameter list
        correctly by counting depth.

        Returns False if the stream ends before finding the match.
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
                        next_tok = stream.peek_at(offset + 1)
                        return next_tok is not None and next_tok.token_type == T.FAT_ARROW
            offset += 1
