from spud.stage_five.stage_five_token_type import StageFiveTokenType as T
from spud.stage_six.identifier import Identifier
from spud.stage_six.parse_error import ParseContextKind, ParseError, ctx
from spud.stage_six.token_stream import TokenStream


def parse_param_list(stream: TokenStream) -> list[Identifier] | ParseError:
    """Parse a comma-separated list of parameter identifiers.

    An empty list is valid — ``()`` means no parameters. Each
    parameter must be a bare identifier (no defaults, no type
    annotations, no destructuring).
    """
    params: list[Identifier] = []
    if stream.peek_type() == T.PAREN_RIGHT:
        return params
    first = stream.expect(T.IDENTIFIER, context=ctx(ParseContextKind.FUNCTION_PARAMS))
    if isinstance(first, ParseError):
        return first
    params.append(Identifier(position=first.position, end=first.position, name=first.value))
    while stream.peek_type() == T.COMMA:
        stream.consume()
        param = stream.expect(T.IDENTIFIER, context=ctx(ParseContextKind.FUNCTION_PARAMS))
        if isinstance(param, ParseError):
            return param
        params.append(Identifier(position=param.position, end=param.position, name=param.value))
    return params
