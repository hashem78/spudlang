"""Semantic tokens provider for the spud LSP server.

Translates spud's internal understanding of a program (the AST from
stage 6 and the resolved environment from stage 7) into the LSP
semantic tokens wire format so editors can apply syntax highlighting.

The handler performs two passes over the source:

1. **Token stream pass** — scans the stage 5 token list for keywords
   (``if``, ``for``, ``else``, …) and operators (``+``, ``:=``,
   ``==``, …).  These tokens are consumed during parsing and do not
   survive into the AST, so the raw token stream is the only source.

2. **AST pass** — walks the AST to classify identifiers, literals,
   and function calls.  An ``Identifier`` named ``f`` could be a
   function, a parameter, or a variable — only the resolved
   environment knows which, so this pass consults it to pick the
   correct token type.

The results from both passes are merged, sorted by source position,
and delta-encoded into the flat integer list the LSP protocol expects.

Delta encoding represents each token as five integers relative to the
previous token::

    [deltaLine, deltaStartChar, length, tokenTypeIndex, modifierBitmask]

When ``deltaLine > 0``, ``deltaStartChar`` is the absolute column
(new line resets the reference point).  When ``deltaLine == 0``,
``deltaStartChar`` is the offset from the previous token's column.

The editor reads this list, maps each ``tokenTypeIndex`` to a name
from the legend (e.g. ``"function"``), and applies the corresponding
color from the user's theme.

Token type legend::

    0 = variable      (plain bindings, for-loop variables)
    1 = function       (function bindings and calls)
    2 = parameter      (function parameters)
    3 = number         (int and float literals)
    4 = string         (string and raw string literals)
    5 = keyword        (if, else, for, in, true, false, …)
    6 = operator       (+, -, :=, ==, …)

Token modifier legend::

    bit 0 = declaration   (binding targets, param definitions, loop variables)
"""

from lsprotocol import types

from spud.core.environment import Environment
from spud.core.keywords import KEYWORDS
from spud.core.operator_precedence import OPERATOR_TOKENS
from spud.stage_five.stage_five_token import StageFiveToken
from spud.stage_seven.resolve_result import ResolveResult
from spud.stage_six.ast_node import ASTNode
from spud.stage_six.binary_op import BinaryOp
from spud.stage_six.binding import Binding
from spud.stage_six.float_literal import FloatLiteral
from spud.stage_six.for_loop import ForLoop
from spud.stage_six.function_call import FunctionCall
from spud.stage_six.function_def import FunctionDef
from spud.stage_six.function_type_expr import FunctionTypeExpr
from spud.stage_six.identifier import Identifier
from spud.stage_six.if_else import IfElse
from spud.stage_six.inline_function_def import InlineFunctionDef
from spud.stage_six.int_literal import IntLiteral
from spud.stage_six.list_literal import ListLiteral
from spud.stage_six.list_type_expr import ListTypeExpr
from spud.stage_six.named_type import NamedType
from spud.stage_six.raw_string_literal import RawStringLiteral
from spud.stage_six.string_literal import StringLiteral
from spud.stage_six.type_expression import TypeExpression
from spud.stage_six.typed_param import TypedParam
from spud.stage_six.unary_op import UnaryOp

VARIABLE = 0
FUNCTION = 1
PARAMETER = 2
NUMBER = 3
STRING = 4
KEYWORD = 5
OPERATOR = 6
TYPE = 7

DECLARATION = 1 << 0

TOKEN_TYPES = ["variable", "function", "parameter", "number", "string", "keyword", "operator", "type"]
TOKEN_MODIFIERS = ["declaration"]

LEGEND = types.SemanticTokensLegend(
    token_types=TOKEN_TYPES,
    token_modifiers=TOKEN_MODIFIERS,
)

RawToken = tuple[int, int, int, int, int]


class SemanticTokensHandler:
    """Produces semantic tokens for a spud document.

    Maps spud's internal token types and resolved environment bindings
    to the LSP semantic token format.  The editor uses the returned
    data to color each token according to its semantic role.

    Example — given ``f := (x) => x + 1``::

        f     → function, declaration
        x     → parameter, declaration  (in param list)
        x     → parameter               (in body, looked up via env)
        1     → number
        +     → operator                (from token stream)
        :=    → operator                (from token stream)
    """

    def semantic_tokens(
        self,
        result: ResolveResult,
        tokens: list[StageFiveToken],
    ) -> types.SemanticTokens:
        """Build the full semantic token list for a document.

        :param result: The stage 7 resolve result containing the AST
            and the resolved environment tree.
        :param tokens: The stage 5 token stream for the same document,
            used to locate keywords and operators.
        :returns: A ``SemanticTokens`` response with delta-encoded data.
        """
        raw: list[RawToken] = []
        self._collect_from_tokens(tokens, raw)
        self._collect_from_ast(result.program.body, result.environment, raw)
        raw.sort()
        return types.SemanticTokens(data=_delta_encode(raw))

    def _collect_from_tokens(
        self,
        tokens: list[StageFiveToken],
        out: list[RawToken],
    ) -> None:
        """Scan the stage 5 token stream for keywords and operators."""
        for tok in tokens:
            if tok.token_type in KEYWORDS:
                out.append((tok.position.line, tok.position.column, len(tok.value), KEYWORD, 0))
            elif tok.token_type in OPERATOR_TOKENS:
                out.append((tok.position.line, tok.position.column, len(tok.value), OPERATOR, 0))

    def _collect_from_ast(
        self,
        nodes: list[ASTNode],
        env: Environment[ASTNode],
        out: list[RawToken],
    ) -> None:
        """Walk a list of AST nodes, emitting semantic tokens for each."""
        for node in nodes:
            self._visit(node, env, out)

    def _visit(
        self,
        node: ASTNode,
        env: Environment[ASTNode],
        out: list[RawToken],
    ) -> None:
        """Emit semantic tokens for a single AST node and recurse into children."""
        match node:
            case Binding(target=target, type_annotation=type_ann, value=value):
                is_func = isinstance(value, FunctionDef | InlineFunctionDef)
                token_type = FUNCTION if is_func else VARIABLE
                out.append((target.position.line, target.position.column, len(target.name), token_type, DECLARATION))
                _collect_type_tokens(type_ann, out)
                self._visit(value, env, out)

            case FunctionDef(params=params, return_type=return_type, body=body):
                child_env = _find_child_env_with_params(env, params)
                for p in params:
                    out.append((p.name.position.line, p.name.position.column, len(p.name.name), PARAMETER, DECLARATION))
                    _collect_type_tokens(p.type_annotation, out)
                _collect_type_tokens(return_type, out)
                self._collect_from_ast(body, child_env, out)

            case InlineFunctionDef(params=params, return_type=return_type, body=body):
                child_env = _find_child_env_with_params(env, params)
                for p in params:
                    out.append((p.name.position.line, p.name.position.column, len(p.name.name), PARAMETER, DECLARATION))
                    _collect_type_tokens(p.type_annotation, out)
                _collect_type_tokens(return_type, out)
                self._visit(body, child_env, out)

            case ForLoop(variable=variable, variable_type=variable_type, iterable=iterable, body=body):
                out.append(
                    (variable.position.line, variable.position.column, len(variable.name), VARIABLE, DECLARATION)
                )
                _collect_type_tokens(variable_type, out)
                self._visit(iterable, env, out)
                child_env = _find_child_env_with_binding(env, variable.name)
                self._collect_from_ast(body, child_env, out)

            case IfElse(branches=branches, else_body=else_body):
                child_idx = 0
                for branch in branches:
                    self._visit(branch.condition, env, out)
                    child_env = env.children[child_idx] if child_idx < len(env.children) else env
                    self._collect_from_ast(branch.body, child_env, out)
                    child_idx += 1
                if else_body:
                    child_env = env.children[child_idx] if child_idx < len(env.children) else env
                    self._collect_from_ast(else_body, child_env, out)

            case FunctionCall(callee=callee, args=args):
                out.append((callee.position.line, callee.position.column, len(callee.name), FUNCTION, 0))
                for arg in args:
                    self._visit(arg, env, out)

            case Identifier(name=name):
                token_type = _classify_identifier(name, env)
                out.append((node.position.line, node.position.column, len(name), token_type, 0))

            case IntLiteral(value=value):
                out.append((node.position.line, node.position.column, len(str(value)), NUMBER, 0))

            case FloatLiteral(value=value):
                out.append((node.position.line, node.position.column, len(str(value)), NUMBER, 0))

            case StringLiteral(value=value):
                out.append((node.position.line, node.position.column, len(value) + 2, STRING, 0))

            case RawStringLiteral(value=value):
                out.append((node.position.line, node.position.column, len(value) + 2, STRING, 0))

            case BinaryOp(left=left, right=right):
                self._visit(left, env, out)
                self._visit(right, env, out)

            case UnaryOp(operand=operand):
                self._visit(operand, env, out)

            case ListLiteral(elements=elements):
                for elem in elements:
                    self._visit(elem, env, out)


def _collect_type_tokens(type_expr: TypeExpression, out: list[RawToken]) -> None:
    """Emit semantic tokens for a type expression and its children."""
    match type_expr:
        case NamedType(name=name):
            out.append((type_expr.position.line, type_expr.position.column, len(name), TYPE, 0))
        case ListTypeExpr(element=element):
            out.append((type_expr.position.line, type_expr.position.column, len("List"), TYPE, 0))
            _collect_type_tokens(element, out)
        case FunctionTypeExpr(params=params, returns=returns):
            out.append((type_expr.position.line, type_expr.position.column, len("Function"), TYPE, 0))
            for p in params:
                _collect_type_tokens(p, out)
            _collect_type_tokens(returns, out)


def _classify_identifier(name: str, env: Environment[ASTNode]) -> int:
    """Determine the semantic token type for an identifier reference."""
    bound = env.lookup(name)
    if bound is None:
        return VARIABLE
    match bound:
        case Binding(value=value) if isinstance(value, FunctionDef | InlineFunctionDef):
            return FUNCTION
        case Identifier():
            return PARAMETER
        case _:
            return VARIABLE


def _find_child_env_with_params(
    env: Environment[ASTNode],
    params: list[TypedParam],
) -> Environment[ASTNode]:
    """Find the child environment that contains the given function parameters."""
    if not params:
        for child in env.children:
            if not child.bindings:
                return child
        return env
    first_param = params[0].name.name
    for child in env.children:
        if child.contains(first_param):
            return child
    return env


def _find_child_env_with_binding(
    env: Environment[ASTNode],
    name: str,
) -> Environment[ASTNode]:
    """Find the child environment that contains a binding for *name*."""
    for child in env.children:
        if child.contains(name):
            return child
    return env


def _delta_encode(tokens: list[RawToken]) -> list[int]:
    """Convert sorted absolute-position tokens into LSP delta encoding."""
    data: list[int] = []
    prev_line = 0
    prev_col = 0
    for line, col, length, token_type, modifiers in tokens:
        delta_line = line - prev_line
        delta_col = col - prev_col if delta_line == 0 else col
        data.extend([delta_line, delta_col, length, token_type, modifiers])
        prev_line = line
        prev_col = col
    return data
