from spud.stage_five.stage_five_token_type import StageFiveTokenType as T
from spud.stage_six.ast_node import ASTNode
from spud.stage_six.function_def import FunctionDef
from spud.stage_six.parse_errors.parse_context import ctx
from spud.stage_six.parse_errors.parse_context_kind import ParseContextKind
from spud.stage_six.parse_errors.parse_error import ParseError, with_context
from spud.stage_six.parser_protocol import IParser
from spud.stage_six.parsers.param_list_parser import parse_param_list
from spud.stage_six.parsers.type_parser import parse_type
from spud.stage_six.token_stream import TokenStream


class FunctionDefParser:
    """Parse a block function definition with typed parameters and return type.

    Parses the grammar rule::

        function_def = '(' param_list ')' ':' type FAT_ARROW NEWLINE block
        param_list   = ( IDENTIFIER ':' type ( COMMA IDENTIFIER ':' type )* )?

    Function definitions in spud are always anonymous — they only
    get a name when bound via ``:=``. The ``BindingParser`` handles
    detecting whether a value is a function def and delegates here.

    The body is always an indented block. Inline single-expression
    functions are handled by ``ExpressionParser`` as
    ``InlineFunctionDef`` nodes.

    Examples::

        (x : Int) : Int =>
          x + 1

        (a : Int, b : Int) : Int =>
          result : Int := a + b
          result

        () : Unit =>
          42
    """

    def __init__(self, block_parser: IParser[list[ASTNode]]):
        self._block_parser = block_parser

    def parse(self, stream: TokenStream) -> FunctionDef | ParseError:
        """Consume ``( params ) : ReturnType => NEWLINE`` and parse the body block."""
        paren_tok = stream.expect(T.PAREN_LEFT, context=ctx(ParseContextKind.FUNCTION_PARAMS))
        if isinstance(paren_tok, ParseError):
            return paren_tok
        params = parse_param_list(stream)
        if isinstance(params, ParseError):
            return params
        rparen = stream.expect(T.PAREN_RIGHT, context=ctx(ParseContextKind.FUNCTION_PARAMS))
        if isinstance(rparen, ParseError):
            return rparen
        colon = stream.expect(T.COLON, context=ctx(ParseContextKind.RETURN_TYPE))
        if isinstance(colon, ParseError):
            return colon
        return_type = parse_type(stream)
        if isinstance(return_type, ParseError):
            return return_type
        fat_arrow = stream.expect(T.FAT_ARROW, context=ctx(ParseContextKind.FUNCTION_BODY))
        if isinstance(fat_arrow, ParseError):
            return fat_arrow
        nl = stream.expect(T.NEW_LINE, context=ctx(ParseContextKind.FUNCTION_BODY))
        if isinstance(nl, ParseError):
            return nl
        body = self._block_parser.parse(stream)
        if isinstance(body, ParseError):
            return with_context(body, ctx(ParseContextKind.FUNCTION_BODY))
        end = body[-1].end if body else fat_arrow.position
        return FunctionDef(position=paren_tok.position, end=end, params=params, return_type=return_type, body=body)
