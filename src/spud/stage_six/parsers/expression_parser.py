from spud.core.position import Position
from spud.stage_five.stage_five_token import StageFiveToken
from spud.stage_five.stage_five_token_type import StageFiveTokenType as T
from spud.stage_six.ast_node import ASTNode
from spud.stage_six.binary_op import BinaryOp
from spud.stage_six.boolean_literal import BooleanLiteral
from spud.stage_six.function_call import FunctionCall
from spud.stage_six.identifier import Identifier
from spud.stage_six.numeric_literal import NumericLiteral
from spud.stage_six.parse_error import ParseContext, ParseContextKind, ParseError, ParseErrorKind, ctx, with_context
from spud.stage_six.raw_string_literal import RawStringLiteral
from spud.stage_six.string_literal import StringLiteral
from spud.stage_six.token_stream import TokenStream

# Operator precedence table, ordered from lowest to highest binding
# strength. Each entry is (operator_tokens, max_applications).
#
# max_applications controls associativity:
#   None  — left-associative, loops until no more matching operators
#   1     — non-associative, at most one operator allowed (no chaining)
#
# The table is walked by _parse_binary: level 0 is the loosest
# (logical or), and once all levels are exhausted it falls through
# to _parse_unary. Adding a new precedence level is just appending
# a tuple here — no new method needed.
#
#   Level  Operators                          Associativity
#   ─────  ─────────────────────────────────  ─────────────
#   0      ||                                 left
#   1      &&                                 left
#   2      == != < > <= >=                    none (single)
#   3      + -                                left
#   4      * / %                              left
#
_PRECEDENCE: list[tuple[set[T], int | None]] = [
    ({T.LOGICAL_OR}, None),
    ({T.LOGICAL_AND}, None),
    ({T.EQUALS, T.NOT_EQUALS, T.LESS_THAN, T.GREATER_THAN, T.LESS_THAN_OR_EQUAL, T.GREATER_THAN_OR_EQUAL}, 1),
    ({T.PLUS, T.MINUS}, None),
    ({T.MULTIPLY, T.DIVIDE, T.MODULO}, None),
]


class ExpressionParser:
    """Recursive descent expression parser with data-driven precedence.

    Parses the expression grammar::

        expression     = binary(level=0)
        binary(n)      = binary(n+1) ( OP binary(n+1) )*   [if n < len(table)]
        binary(n)      = unary                              [if n >= len(table)]
        unary          = MINUS unary | primary
        primary        = IDENTIFIER ( '(' arg_list ')' )?
                       | STRING | RAW_STRING | TRUE | FALSE
                       | '(' expression ')'

    The precedence table drives ``_parse_binary``. At each level the
    method parses its left operand at the next-tighter level, then
    loops while the current token matches that level's operator set,
    building left-associative ``BinaryOp`` nodes. Non-associative
    levels (comparisons) cap the loop at one iteration.

    When all levels are exhausted, ``_parse_unary`` handles prefix
    minus by desugaring ``-x`` into ``0 - x``. Finally
    ``_parse_primary`` handles atoms: identifiers (which may be
    numeric literals or function calls depending on what follows),
    string/boolean literals, and parenthesized sub-expressions.
    """

    def parse(self, stream: TokenStream) -> ASTNode | ParseError:
        """Entry point. Parses a single expression from the stream."""
        return self._parse_binary(stream, level=0)

    def _parse_binary(self, stream: TokenStream, level: int) -> ASTNode | ParseError:
        """Parse a binary expression at the given precedence level.

        Recurses to ``level + 1`` for operands, binding tighter
        operators first. When ``level`` exceeds the table, falls
        through to ``_parse_unary`` — the tightest binding level
        before atoms.

        For ``a + b * c`` at level 3 (addition):
          1. Recurse to level 4 (multiplication) for left operand
          2. Level 4 recurses to unary, which returns ``a``
          3. Level 4 sees no ``*``, returns ``a`` to level 3
          4. Level 3 sees ``+``, consumes it
          5. Recurse to level 4 for right operand
          6. Level 4 parses ``b * c`` into ``BinaryOp(b, *, c)``
          7. Level 3 builds ``BinaryOp(a, +, BinaryOp(b, *, c))``
        """
        # Base case: all precedence levels exhausted, parse an atom.
        if level >= len(_PRECEDENCE):
            return self._parse_unary(stream)

        ops, max_ops = _PRECEDENCE[level]

        # Parse the left operand at the next-tighter precedence level.
        left = self._parse_binary(stream, level + 1)
        if isinstance(left, ParseError):
            return left

        # Consume operators at this level, building left-associative
        # BinaryOp nodes. Non-associative levels (max_ops=1) stop
        # after one operator — ``a < b < c`` is a parse error because
        # the second ``<`` won't be consumed here, and the caller
        # won't expect it either.
        count = 0
        while stream.peek_type() in ops and (max_ops is None or count < max_ops):
            op_tok = stream.consume()
            if isinstance(op_tok, ParseError):
                return op_tok
            right = self._parse_binary(stream, level + 1)
            if isinstance(right, ParseError):
                return right
            left = BinaryOp(position=left.position, end=right.end, left=left, operator=op_tok.value, right=right)
            count += 1
        return left

    def _parse_unary(self, stream: TokenStream) -> ASTNode | ParseError:
        """Parse a unary prefix expression.

        Currently only handles unary minus. Desugars ``-x`` into
        ``BinaryOp(0, "-", x)`` so the AST doesn't need a separate
        unary node type. Recurses into itself for chained negation
        (``--x`` becomes ``BinaryOp(0, "-", BinaryOp(0, "-", x))``).

        If the current token is not ``-``, falls through to
        ``_parse_primary``.
        """
        if stream.peek_type() == T.MINUS:
            op_tok = stream.consume()
            if isinstance(op_tok, ParseError):
                return op_tok
            operand = self._parse_unary(stream)
            if isinstance(operand, ParseError):
                return operand
            zero = NumericLiteral(position=op_tok.position, end=op_tok.position, value=0)
            return BinaryOp(position=op_tok.position, end=operand.end, left=zero, operator="-", right=operand)
        return self._parse_primary(stream)

    def _parse_primary(self, stream: TokenStream) -> ASTNode | ParseError:
        """Parse an atomic expression — the tightest binding level.

        Handles six cases based on the current token:

        ``IDENTIFIER``
            Could be three things depending on what follows:
            - All digits (``42``) → ``NumericLiteral``. Stage three
              groups character runs into identifiers, so numbers
              arrive here as identifiers with digit-only values.
            - Followed by ``(`` → function call, dispatched to
              ``_parse_function_call``.
            - Otherwise → bare ``Identifier``.

        ``STRING`` / ``RAW_STRING``
            Consumed and wrapped in the corresponding literal node.

        ``TRUE`` / ``FALSE``
            Consumed and wrapped as ``BooleanLiteral``.

        ``PAREN_LEFT``
            Grouped sub-expression: consume ``(``, recursively parse
            a full expression, expect ``)``. The parentheses are
            discarded — they only affect parse-time grouping.

        Anything else
            Returns a ``ParseError`` — the token cannot start an
            expression.
        """
        tok = stream.peek()
        if tok is None:
            return ParseError(
                kind=ParseErrorKind.UNEXPECTED_END,
                position=Position(line=0, column=0),
                context=ctx(ParseContextKind.EXPRESSION),
            )

        match tok.token_type:
            case T.IDENTIFIER:
                stream.consume()
                if tok.value.isdigit():
                    return NumericLiteral(position=tok.position, end=tok.position, value=int(tok.value))
                if stream.peek_type() == T.PAREN_LEFT:
                    return self._parse_function_call(stream, tok)
                return Identifier(position=tok.position, end=tok.position, name=tok.value)

            case T.STRING:
                stream.consume()
                is_double = tok.value.startswith('"')
                is_single = tok.value.startswith("'")
                if (is_double and not tok.value.endswith('"')) or (is_single and not tok.value.endswith("'")):
                    return ParseError(
                        kind=ParseErrorKind.UNEXPECTED_END,
                        position=tok.position,
                        context=ctx(ParseContextKind.UNTERMINATED_STRING),
                    )
                return StringLiteral(position=tok.position, end=tok.position, value=tok.value)

            case T.RAW_STRING:
                stream.consume()
                if not tok.value.endswith("`"):
                    return ParseError(
                        kind=ParseErrorKind.UNEXPECTED_END,
                        position=tok.position,
                        context=ctx(ParseContextKind.UNTERMINATED_RAW_STRING),
                    )
                return RawStringLiteral(position=tok.position, end=tok.position, value=tok.value)

            case T.TRUE:
                stream.consume()
                return BooleanLiteral(position=tok.position, end=tok.position, value=True)

            case T.FALSE:
                stream.consume()
                return BooleanLiteral(position=tok.position, end=tok.position, value=False)

            case T.PAREN_LEFT:
                stream.consume()
                paren_ctx = ParseContext(kind=ParseContextKind.UNTERMINATED_DELIMITER, delimiter=T.PAREN_LEFT)
                expr = self.parse(stream)
                if isinstance(expr, ParseError):
                    return with_context(expr, paren_ctx)
                rparen = stream.expect(T.PAREN_RIGHT, context=paren_ctx)
                if isinstance(rparen, ParseError):
                    return rparen
                return expr.model_copy(update={"end": rparen.position})

            case _:
                return ParseError(
                    kind=ParseErrorKind.UNEXPECTED_TOKEN,
                    position=tok.position,
                    got=tok.token_type,
                    context=ctx(ParseContextKind.EXPRESSION),
                )

    def _parse_function_call(self, stream: TokenStream, callee_tok: StageFiveToken) -> FunctionCall | ParseError:
        """Parse a function call after the callee identifier was consumed.

        The callee identifier has already been consumed by
        ``_parse_primary`` (it peeked at the ``(`` to decide this
        is a call). This method consumes the argument list:
        ``'(' expression (',' expression)* ')'``.

        An empty argument list (``foo()``) is valid — the ``(`` is
        immediately followed by ``)``.

        Each argument is a full expression (parsed via ``self.parse``),
        so ``foo(a + b, c * d)`` correctly nests the binary ops
        inside the argument list.
        """
        stream.expect(T.PAREN_LEFT, context=ctx(ParseContextKind.FUNCTION_ARGS))
        args: list[ASTNode] = []
        if stream.peek_type() != T.PAREN_RIGHT:
            first = self.parse(stream)
            if isinstance(first, ParseError):
                return with_context(first, ctx(ParseContextKind.FUNCTION_ARGS))
            args.append(first)
            while stream.peek_type() == T.COMMA:
                stream.consume()
                arg = self.parse(stream)
                if isinstance(arg, ParseError):
                    return with_context(arg, ctx(ParseContextKind.FUNCTION_ARGS))
                args.append(arg)
        paren_ctx = ParseContext(kind=ParseContextKind.UNTERMINATED_DELIMITER, delimiter=T.PAREN_LEFT)
        rparen = stream.expect(T.PAREN_RIGHT, context=paren_ctx)
        if isinstance(rparen, ParseError):
            return rparen
        callee = Identifier(position=callee_tok.position, end=callee_tok.position, name=callee_tok.value)
        return FunctionCall(position=callee_tok.position, end=rparen.position, callee=callee, args=args)
