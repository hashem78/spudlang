from spud.stage_five import StageFiveTokenType as T
from spud.stage_six import FunctionTypeExpr, ListTypeExpr, NamedType, TokenStream, TypeExpression
from spud.stage_six.parse_errors import ParseContext, ParseContextKind, ParseError, ctx


def parse_type(stream: TokenStream) -> TypeExpression | ParseError:
    """Parse a type expression.

    Grammar::

        type          = IDENTIFIER ( '[' type_args ']' )?
        type_args     = type ( ',' type )*

    Named types: ``Int``, ``Float``, ``String``, ``Bool``, ``Unit``

    Generic types:
        ``List[Int]`` — list with element type
        ``Function[[Int, String], Bool]`` — function taking
        ``(Int, String)`` and returning ``Bool``. The first
        argument is a bracketed list of parameter types, the
        second is the return type.
    """
    name_tok = stream.expect(T.IDENTIFIER, context=ctx(ParseContextKind.TYPE_ANNOTATION))
    if isinstance(name_tok, ParseError):
        return name_tok

    if stream.peek_type() != T.BRACKET_LEFT:
        return NamedType(position=name_tok.position, end=name_tok.position, name=name_tok.value)

    match name_tok.value:
        case "List":
            return _parse_list_type(stream, name_tok)
        case "Function":
            return _parse_function_type(stream, name_tok)
        case _:
            return NamedType(position=name_tok.position, end=name_tok.position, name=name_tok.value)


def _parse_list_type(stream, name_tok):
    """Parse ``List[element_type]``."""
    stream.expect(T.BRACKET_LEFT, context=ctx(ParseContextKind.TYPE_ANNOTATION))
    element = parse_type(stream)
    if isinstance(element, ParseError):
        return element
    rbracket = stream.expect(
        T.BRACKET_RIGHT,
        context=ParseContext(kind=ParseContextKind.UNTERMINATED_DELIMITER, delimiter=T.BRACKET_LEFT),
    )
    if isinstance(rbracket, ParseError):
        return rbracket
    return ListTypeExpr(position=name_tok.position, end=rbracket.position, element=element)


def _parse_function_type(stream, name_tok):
    """Parse ``Function[[param_types], return_type]``.

    The first element is a bracketed list of parameter types,
    the second element is the return type::

        Function[[Int, String], Bool]
        Function[[], Unit]
    """
    stream.expect(T.BRACKET_LEFT, context=ctx(ParseContextKind.TYPE_ANNOTATION))

    inner_lbracket = stream.expect(T.BRACKET_LEFT, context=ctx(ParseContextKind.TYPE_ANNOTATION))
    if isinstance(inner_lbracket, ParseError):
        return inner_lbracket

    params: list[TypeExpression] = []
    if stream.peek_type() != T.BRACKET_RIGHT:
        first = parse_type(stream)
        if isinstance(first, ParseError):
            return first
        params.append(first)
        while stream.peek_type() == T.COMMA:
            stream.consume()
            param = parse_type(stream)
            if isinstance(param, ParseError):
                return param
            params.append(param)

    inner_rbracket = stream.expect(
        T.BRACKET_RIGHT,
        context=ParseContext(kind=ParseContextKind.UNTERMINATED_DELIMITER, delimiter=T.BRACKET_LEFT),
    )
    if isinstance(inner_rbracket, ParseError):
        return inner_rbracket

    comma = stream.expect(T.COMMA, context=ctx(ParseContextKind.TYPE_ANNOTATION))
    if isinstance(comma, ParseError):
        return comma

    returns = parse_type(stream)
    if isinstance(returns, ParseError):
        return returns

    rbracket = stream.expect(
        T.BRACKET_RIGHT,
        context=ParseContext(kind=ParseContextKind.UNTERMINATED_DELIMITER, delimiter=T.BRACKET_LEFT),
    )
    if isinstance(rbracket, ParseError):
        return rbracket

    return FunctionTypeExpr(
        position=name_tok.position,
        end=rbracket.position,
        params=params,
        returns=returns,
    )
