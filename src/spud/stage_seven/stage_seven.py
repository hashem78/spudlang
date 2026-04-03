from structlog import BoundLogger

from spud.core.environment import Environment
from spud.core.position import Position
from spud.stage_seven.resolve_error import ResolveError, ResolveErrorKind
from spud.stage_seven.resolve_result import ResolveResult
from spud.stage_six.ast_node import ASTNode
from spud.stage_six.binary_op import BinaryOp
from spud.stage_six.binding import Binding
from spud.stage_six.condition_branch import ConditionBranch
from spud.stage_six.for_loop import ForLoop
from spud.stage_six.function_call import FunctionCall
from spud.stage_six.function_def import FunctionDef
from spud.stage_six.identifier import Identifier
from spud.stage_six.if_else import IfElse
from spud.stage_six.inline_function_def import InlineFunctionDef
from spud.stage_six.list_literal import ListLiteral
from spud.stage_six.program import Program
from spud.stage_six.unary_op import UnaryOp


class StageSeven:
    def __init__(self, logger: BoundLogger):
        self._logger = logger

    def resolve(self, program: Program) -> ResolveResult:
        errors: list[ResolveError] = []
        env: Environment[ASTNode] = Environment()
        for node in program.body:
            env = self._resolve_node(node, env, errors)
        return ResolveResult(errors=errors, environment=env)

    def _resolve_node(
        self,
        node: ASTNode,
        env: Environment[ASTNode],
        errors: list[ResolveError],
    ) -> Environment[ASTNode]:
        match node:
            case Binding(target=target, value=value):
                return self._resolve_binding(target, value, node, env, errors)
            case FunctionDef(params=params, body=body):
                self._resolve_function(params, body, env, errors)
                return env
            case InlineFunctionDef(params=params, body=body):
                self._resolve_function(params, [body], env, errors)
                return env
            case ForLoop(variable=variable, iterable=iterable, body=body):
                self._resolve_node(iterable, env, errors)
                child = env.child()
                child = self._define_checked(variable.name, variable.position, node, child, env, errors)
                self._resolve_body(body, child, errors)
                return env
            case IfElse(branches=branches, else_body=else_body):
                for branch in branches:
                    self._resolve_branch(branch, env, errors)
                if else_body:
                    child = env.child()
                    self._resolve_body(else_body, child, errors)
                return env
            case Identifier(name=name):
                if env.lookup(name) is None:
                    errors.append(
                        ResolveError(
                            kind=ResolveErrorKind.UNDEFINED_VARIABLE,
                            position=node.position,
                            name=name,
                        )
                    )
                return env
            case FunctionCall(callee=callee, args=args):
                self._resolve_node(callee, env, errors)
                for arg in args:
                    self._resolve_node(arg, env, errors)
                return env
            case BinaryOp(left=left, right=right):
                self._resolve_node(left, env, errors)
                self._resolve_node(right, env, errors)
                return env
            case UnaryOp(operand=operand):
                self._resolve_node(operand, env, errors)
                return env
            case ListLiteral(elements=elements):
                for elem in elements:
                    self._resolve_node(elem, env, errors)
                return env
            case _:
                return env

    def _resolve_binding(
        self,
        target: Identifier,
        value: ASTNode,
        node: ASTNode,
        env: Environment[ASTNode],
        errors: list[ResolveError],
    ) -> Environment[ASTNode]:
        has_error = self._check_binding(target.name, target.position, env, errors)
        is_function = isinstance(value, FunctionDef | InlineFunctionDef)
        if is_function and not has_error:
            env = env.with_binding(target.name, node)
        self._resolve_node(value, env, errors)
        if not is_function and not has_error:
            env = env.with_binding(target.name, node)
        return env

    def _resolve_function(
        self,
        params: list[Identifier],
        body: list[ASTNode],
        env: Environment[ASTNode],
        errors: list[ResolveError],
    ) -> None:
        child = env.child()
        for param in params:
            child = self._define_checked(param.name, param.position, param, child, env, errors)
        self._resolve_body(body, child, errors)

    def _resolve_branch(
        self,
        branch: ConditionBranch,
        env: Environment[ASTNode],
        errors: list[ResolveError],
    ) -> None:
        self._resolve_node(branch.condition, env, errors)
        child = env.child()
        self._resolve_body(branch.body, child, errors)

    def _resolve_body(
        self,
        body: list[ASTNode],
        env: Environment[ASTNode],
        errors: list[ResolveError],
    ) -> Environment[ASTNode]:
        for node in body:
            env = self._resolve_node(node, env, errors)
        return env

    def _check_binding(
        self,
        name: str,
        position: Position,
        env: Environment[ASTNode],
        errors: list[ResolveError],
    ) -> bool:
        if env.contains(name):
            errors.append(
                ResolveError(
                    kind=ResolveErrorKind.DUPLICATE_BINDING,
                    position=position,
                    name=name,
                )
            )
            return True
        if env.lookup(name) is not None:
            errors.append(
                ResolveError(
                    kind=ResolveErrorKind.SHADOWED_BINDING,
                    position=position,
                    name=name,
                )
            )
            return True
        return False

    def _define_checked(
        self,
        name: str,
        position: Position,
        node: ASTNode,
        env: Environment[ASTNode],
        parent_env: Environment[ASTNode],
        errors: list[ResolveError],
    ) -> Environment[ASTNode]:
        if env.contains(name):
            errors.append(
                ResolveError(
                    kind=ResolveErrorKind.DUPLICATE_BINDING,
                    position=position,
                    name=name,
                )
            )
            return env
        if parent_env.lookup(name) is not None:
            errors.append(
                ResolveError(
                    kind=ResolveErrorKind.SHADOWED_BINDING,
                    position=position,
                    name=name,
                )
            )
            return env
        return env.with_binding(name, node)
