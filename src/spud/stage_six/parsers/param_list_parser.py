from spud.stage_five.stage_five_token_type import StageFiveTokenType as T
from spud.stage_six.identifier import Identifier
from spud.stage_six.parse_error import ParseContextKind, ParseError, ctx
from spud.stage_six.parsers.type_parser import parse_type
from spud.stage_six.token_stream import TokenStream
from spud.stage_six.typed_param import TypedParam


def parse_param_list(stream: TokenStream) -> list[TypedParam] | ParseError:
    """Parse a comma-separated list of typed parameters.

    Grammar::

        param_list = ( IDENTIFIER ':' type ( ',' IDENTIFIER ':' type )* )?
    """
    params: list[TypedParam] = []
    if stream.peek_type() == T.PAREN_RIGHT:
        return params
    first = _parse_one_param(stream)
    if isinstance(first, ParseError):
        return first
    params.append(first)
    while stream.peek_type() == T.COMMA:
        stream.consume()
        param = _parse_one_param(stream)
        if isinstance(param, ParseError):
            return param
        params.append(param)
    return params


def _parse_one_param(stream: TokenStream) -> TypedParam | ParseError:
    name_tok = stream.expect(T.IDENTIFIER, context=ctx(ParseContextKind.FUNCTION_PARAMS))
    if isinstance(name_tok, ParseError):
        return name_tok
    colon = stream.expect(T.COLON, context=ctx(ParseContextKind.TYPE_ANNOTATION))
    if isinstance(colon, ParseError):
        return colon
    type_ann = parse_type(stream)
    if isinstance(type_ann, ParseError):
        return type_ann
    return TypedParam(
        name=Identifier(position=name_tok.position, end=name_tok.position, name=name_tok.value),
        type_annotation=type_ann,
    )
