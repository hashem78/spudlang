from spud.core import Environment
from spud.core.types import (
    BoolType,
    FunctionType,
    ListType,
    SpudType,
    UnitType,
)
from spud.stage_six import (
    BinaryOp,
    Binding,
    ForLoop,
    FunctionCall,
    FunctionDef,
    IfElse,
    InlineFunctionDef,
    ListLiteral,
    Program,
    UnaryOp,
)
from spud_check.checkers import NodeChecker
from spud_check.operator_types import BINARY_OP_TYPES, UNARY_OP_TYPES
from spud_check.type_check_result import TypeCheckResult
from spud_check.type_errors import (
    ArgumentCountMismatchError,
    ArgumentTypeMismatchError,
    BranchTypeMismatchError,
    ConditionNotBoolError,
    ElementTypeMismatchError,
    HeterogeneousListError,
    NotCallableError,
    NotIterableError,
    OperatorTypeError,
    ReturnTypeMismatchError,
    TypeError,
    TypeMismatchError,
    UnaryOperatorTypeError,
)
from spud_check.type_resolver import resolve_type
from spud_check.typed_nodes import (
    TypedBinaryOp,
    TypedBinding,
    TypedConditionBranch,
    TypedForLoop,
    TypedFunctionCall,
    TypedFunctionDef,
    TypedIfElse,
    TypedInlineFunctionDef,
    TypedListLiteral,
    TypedNode,
    TypedParam,
    TypedProgram,
    TypedUnaryOp,
)


class TypeChecker:
    """Type checker for spud programs.

    Single-pass AST walk that threads an Environment[SpudType]
    through the tree. Resolves type annotations, checks consistency,
    and builds a parallel typed AST.
    """

    def __init__(self, node_checker: "NodeChecker | None" = None):
        from spud_check.checkers import build_node_checker

        self._node_checker = node_checker if node_checker is not None else build_node_checker(self)

    def check(self, program: Program) -> TypeCheckResult:
        errors: list[TypeError] = []
        env: Environment[SpudType] = Environment()
        typed_body: list[TypedNode] = []

        for node in program.body:
            typed_node, env = self._node_checker.dispatch(node, env, errors)
            typed_body.append(typed_node)

        typed_program = TypedProgram(
            resolved_type=UnitType(),
            position=program.position,
            end=program.end,
            body=typed_body,
        )
        return TypeCheckResult(errors=errors, typed_program=typed_program)

    def _check_binding(
        self,
        node: Binding,
        env: Environment[SpudType],
        errors: list[TypeError],
    ) -> tuple[TypedBinding, Environment[SpudType]]:
        declared = resolve_type(node.type_annotation, errors)

        is_function = isinstance(node.value, FunctionDef | InlineFunctionDef)
        if is_function:
            env = env.with_binding(node.target.name, declared)

        typed_value, env = self._node_checker.dispatch(node.value, env, errors)

        if typed_value.resolved_type != declared:
            errors.append(
                TypeMismatchError(
                    position=node.position,
                    name=node.target.name,
                    expected=declared.kind,
                    actual=typed_value.resolved_type.kind,
                )
            )

        if not is_function:
            env = env.with_binding(node.target.name, declared)

        return TypedBinding(
            resolved_type=declared,
            position=node.position,
            end=node.end,
            target_name=node.target.name,
            type_annotation=node.type_annotation,
            value=typed_value,
        ), env

    def _check_binary_op(
        self,
        node: BinaryOp,
        env: Environment[SpudType],
        errors: list[TypeError],
    ) -> TypedBinaryOp:
        typed_left, _ = self._node_checker.dispatch(node.left, env, errors)
        typed_right, _ = self._node_checker.dispatch(node.right, env, errors)

        key = (node.operator, typed_left.resolved_type.kind, typed_right.resolved_type.kind)
        result_type = BINARY_OP_TYPES.get(key)

        if result_type is None:
            errors.append(
                OperatorTypeError(
                    position=node.position,
                    operator=node.operator,
                    left=typed_left.resolved_type.kind,
                    right=typed_right.resolved_type.kind,
                )
            )
            result_type = UnitType()

        return TypedBinaryOp(
            resolved_type=result_type,
            position=node.position,
            end=node.end,
            left=typed_left,
            operator=node.operator,
            right=typed_right,
        )

    def _check_unary_op(
        self,
        node: UnaryOp,
        env: Environment[SpudType],
        errors: list[TypeError],
    ) -> TypedUnaryOp:
        typed_operand, _ = self._node_checker.dispatch(node.operand, env, errors)

        key = (node.operator, typed_operand.resolved_type.kind)
        result_type = UNARY_OP_TYPES.get(key)

        if result_type is None:
            errors.append(
                UnaryOperatorTypeError(
                    position=node.position,
                    operator=node.operator,
                    operand=typed_operand.resolved_type.kind,
                )
            )
            result_type = UnitType()

        return TypedUnaryOp(
            resolved_type=result_type,
            position=node.position,
            end=node.end,
            operator=node.operator,
            operand=typed_operand,
        )

    def _check_function_call(
        self,
        node: FunctionCall,
        env: Environment[SpudType],
        errors: list[TypeError],
    ) -> TypedFunctionCall:
        callee_type = env.lookup(node.callee.name)

        if callee_type is None or not isinstance(callee_type, FunctionType):
            if callee_type is not None:
                errors.append(
                    NotCallableError(
                        position=node.position,
                        name=node.callee.name,
                    )
                )
            return TypedFunctionCall(
                resolved_type=UnitType(),
                position=node.position,
                end=node.end,
                callee_name=node.callee.name,
                args=[self._node_checker.dispatch(a, env, errors)[0] for a in node.args],
            )

        if len(node.args) != len(callee_type.params):
            errors.append(
                ArgumentCountMismatchError(
                    position=node.position,
                    name=node.callee.name,
                    expected_count=len(callee_type.params),
                    actual_count=len(node.args),
                )
            )

        typed_args: list[TypedNode] = []
        for i, arg in enumerate(node.args):
            typed_arg, _ = self._node_checker.dispatch(arg, env, errors)
            typed_args.append(typed_arg)
            if i < len(callee_type.params) and typed_arg.resolved_type != callee_type.params[i]:
                errors.append(
                    ArgumentTypeMismatchError(
                        position=arg.position,
                        name=node.callee.name,
                        index=i,
                        expected=callee_type.params[i].kind,
                        actual=typed_arg.resolved_type.kind,
                    )
                )

        return TypedFunctionCall(
            resolved_type=callee_type.returns,
            position=node.position,
            end=node.end,
            callee_name=node.callee.name,
            args=typed_args,
        )

    def _check_function_def(
        self,
        node: FunctionDef,
        env: Environment[SpudType],
        errors: list[TypeError],
    ) -> TypedFunctionDef:
        param_types: list[SpudType] = []
        typed_params: list[TypedParam] = []
        child_env = env.child()

        for p in node.params:
            pt = resolve_type(p.type_annotation, errors)
            param_types.append(pt)
            child_env = child_env.with_binding(p.name.name, pt)
            typed_params.append(
                TypedParam(
                    resolved_type=pt, position=p.name.position, end=p.name.end, name=p.name.name, declared_type=pt
                )
            )

        return_type = resolve_type(node.return_type, errors)

        typed_body: list[TypedNode] = []
        for stmt in node.body:
            typed_stmt, child_env = self._node_checker.dispatch(stmt, child_env, errors)
            typed_body.append(typed_stmt)

        if typed_body:
            body_type = typed_body[-1].resolved_type
            if body_type != return_type:
                errors.append(
                    ReturnTypeMismatchError(
                        position=node.position,
                        expected=return_type.kind,
                        actual=body_type.kind,
                    )
                )

        func_type = FunctionType(params=tuple(param_types), returns=return_type)
        return TypedFunctionDef(
            resolved_type=func_type,
            position=node.position,
            end=node.end,
            params=typed_params,
            return_type=return_type,
            body=typed_body,
        )

    def _check_inline_function_def(
        self,
        node: InlineFunctionDef,
        env: Environment[SpudType],
        errors: list[TypeError],
    ) -> TypedInlineFunctionDef:
        param_types: list[SpudType] = []
        typed_params: list[TypedParam] = []
        child_env = env.child()

        for p in node.params:
            pt = resolve_type(p.type_annotation, errors)
            param_types.append(pt)
            child_env = child_env.with_binding(p.name.name, pt)
            typed_params.append(
                TypedParam(
                    resolved_type=pt, position=p.name.position, end=p.name.end, name=p.name.name, declared_type=pt
                )
            )

        return_type = resolve_type(node.return_type, errors)
        typed_body, _ = self._node_checker.dispatch(node.body, child_env, errors)

        if typed_body.resolved_type != return_type:
            errors.append(
                ReturnTypeMismatchError(
                    position=node.position,
                    expected=return_type.kind,
                    actual=typed_body.resolved_type.kind,
                )
            )

        func_type = FunctionType(params=tuple(param_types), returns=return_type)
        return TypedInlineFunctionDef(
            resolved_type=func_type,
            position=node.position,
            end=node.end,
            params=typed_params,
            return_type=return_type,
            body=typed_body,
        )

    def _check_if_else(
        self,
        node: IfElse,
        env: Environment[SpudType],
        errors: list[TypeError],
    ) -> TypedIfElse:
        typed_branches: list[TypedConditionBranch] = []
        branch_types: list[SpudType] = []

        for branch in node.branches:
            typed_cond, _ = self._node_checker.dispatch(branch.condition, env, errors)
            if typed_cond.resolved_type != BoolType():
                errors.append(
                    ConditionNotBoolError(
                        position=branch.condition.position,
                        actual=typed_cond.resolved_type.kind,
                    )
                )

            child_env = env.child()
            typed_body: list[TypedNode] = []
            for stmt in branch.body:
                typed_stmt, child_env = self._node_checker.dispatch(stmt, child_env, errors)
                typed_body.append(typed_stmt)

            branch_type = typed_body[-1].resolved_type if typed_body else UnitType()
            branch_types.append(branch_type)
            typed_branches.append(
                TypedConditionBranch(
                    resolved_type=branch_type,
                    position=branch.position,
                    end=branch.end,
                    condition=typed_cond,
                    body=typed_body,
                )
            )

        typed_else: list[TypedNode] | None = None
        if node.else_body:
            child_env = env.child()
            typed_else = []
            for stmt in node.else_body:
                typed_stmt, child_env = self._node_checker.dispatch(stmt, child_env, errors)
                typed_else.append(typed_stmt)
            else_type = typed_else[-1].resolved_type if typed_else else UnitType()
            branch_types.append(else_type)

        if len(branch_types) >= 2:
            first = branch_types[0]
            for i, bt in enumerate(branch_types[1:], 1):
                if bt != first:
                    errors.append(
                        BranchTypeMismatchError(
                            position=node.position,
                            index=i,
                            expected=first.kind,
                            actual=bt.kind,
                        )
                    )

        result_type = branch_types[0] if branch_types else UnitType()
        return TypedIfElse(
            resolved_type=result_type,
            position=node.position,
            end=node.end,
            branches=typed_branches,
            else_body=typed_else,
        )

    def _check_for_loop(
        self,
        node: ForLoop,
        env: Environment[SpudType],
        errors: list[TypeError],
    ) -> TypedForLoop:
        typed_iterable, _ = self._node_checker.dispatch(node.iterable, env, errors)
        var_type = resolve_type(node.variable_type, errors)

        if not isinstance(typed_iterable.resolved_type, ListType):
            errors.append(
                NotIterableError(
                    position=node.iterable.position,
                    actual=typed_iterable.resolved_type.kind,
                )
            )
        else:
            if typed_iterable.resolved_type.element != var_type:
                errors.append(
                    ElementTypeMismatchError(
                        position=node.variable.position,
                        name=node.variable.name,
                        expected=var_type.kind,
                        actual=typed_iterable.resolved_type.element.kind,
                    )
                )

        child_env = env.child()
        child_env = child_env.with_binding(node.variable.name, var_type)

        typed_body: list[TypedNode] = []
        for stmt in node.body:
            typed_stmt, child_env = self._node_checker.dispatch(stmt, child_env, errors)
            typed_body.append(typed_stmt)

        return TypedForLoop(
            resolved_type=UnitType(),
            position=node.position,
            end=node.end,
            variable_name=node.variable.name,
            variable_type=var_type,
            iterable=typed_iterable,
            body=typed_body,
        )

    def _check_list_literal(
        self,
        node: ListLiteral,
        env: Environment[SpudType],
        errors: list[TypeError],
    ) -> TypedListLiteral:
        typed_elements: list[TypedNode] = []
        for elem in node.elements:
            typed_elem, _ = self._node_checker.dispatch(elem, env, errors)
            typed_elements.append(typed_elem)

        if not typed_elements:
            return TypedListLiteral(
                resolved_type=ListType(element=UnitType()),
                position=node.position,
                end=node.end,
                elements=[],
            )

        first_type = typed_elements[0].resolved_type
        for i, te in enumerate(typed_elements[1:], 1):
            if te.resolved_type != first_type:
                errors.append(
                    HeterogeneousListError(
                        position=te.position,
                        index=i,
                        expected=first_type.kind,
                        actual=te.resolved_type.kind,
                    )
                )

        return TypedListLiteral(
            resolved_type=ListType(element=first_type),
            position=node.position,
            end=node.end,
            elements=typed_elements,
        )
