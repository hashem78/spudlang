from structlog import BoundLogger

from spud.core import Environment, Position
from spud.core.pipeline import PipelineStage
from spud.core.resolve_errors import (
    DuplicateBindingError,
    ResolveError,
    ShadowedBindingError,
    UndefinedVariableError,
)
from spud.stage_seven.resolve_result import ResolveResult
from spud.stage_six import (
    ASTNode,
    BinaryOp,
    Binding,
    ConditionBranch,
    ForLoop,
    FunctionCall,
    FunctionDef,
    Identifier,
    IfElse,
    InlineFunctionDef,
    ListLiteral,
    Program,
    TypedParam,
    UnaryOp,
)


class StageSeven(PipelineStage):
    """Scope resolution pass over a parsed spud program.

    Walks the AST produced by stage 6 and validates that every
    variable reference resolves to a binding, that no name is bound
    twice in the same scope, and that inner scopes do not shadow
    names from outer scopes.

    The resolver is a single-pass, top-to-bottom walk.  It threads
    an immutable :class:`~spud.core.environment.Environment` through
    the tree — each binding produces a new environment snapshot, and
    child scopes branch off via :meth:`Environment.child`.

    **Scope rules:**

    - ``Binding`` adds to the current scope.
    - ``FunctionDef`` / ``InlineFunctionDef`` open a child scope
      with parameters as initial bindings.
    - ``ForLoop`` opens a child scope with the loop variable.
    - Each ``IfElse`` branch (including ``else``) opens its own
      child scope.
    - No shadowing is allowed: a name bound in a child scope must
      not collide with any name in an ancestor scope.
    - No reassignment: binding a name that already exists in the
      same scope is a ``DUPLICATE_BINDING`` error.

    **Self-recursion support:**

    When a binding's value is a function (``FunctionDef`` or
    ``InlineFunctionDef``), the binding name is registered in the
    environment **before** the function body is walked.  This lets
    the function reference itself::

        factorial := (n) =>
          if n == 0
            1
          else
            n * factorial(n - 1)

    For non-function bindings, the value is walked first, so forward
    self-references are correctly rejected::

        x := x + 1    # UNDEFINED_VARIABLE — x is not yet defined

    Example usage::

        >>> from spud.stage_seven.stage_seven import StageSeven
        >>> resolver = StageSeven(logger=logger)
        >>> result = resolver.resolve(program)
        >>> result.errors
        []
        >>> "x" in result.environment.bindings
        True
    """

    def __init__(self, logger: BoundLogger):
        self._logger = logger

    def resolve(self, program: Program) -> ResolveResult:
        """Resolve all scopes in *program* and return the result.

        :param program: The parsed AST from stage 6.
        :returns: A :class:`~spud.stage_seven.resolve_result.ResolveResult`
            containing any semantic errors and the final global
            environment.
        """
        errors: list[ResolveError] = []
        env: Environment[ASTNode] = Environment()
        for node in program.body:
            env = self._resolve_node(node, env, errors)
        updated_program = program.model_copy(update={"errors": [*program.errors, *errors]})
        return ResolveResult(errors=errors, environment=env, program=updated_program)

    def _resolve_node(
        self,
        node: ASTNode,
        env: Environment[ASTNode],
        errors: list[ResolveError],
    ) -> Environment[ASTNode]:
        """Resolve a single AST node and return the (possibly updated) environment.

        Dispatches on the node type via pattern matching.  Nodes that
        introduce bindings (``Binding``) return a new environment with
        the binding added.  Nodes that introduce scopes (``FunctionDef``,
        ``ForLoop``, ``IfElse``) create child environments internally
        but return the **original** environment unchanged — their
        bindings do not leak into the enclosing scope.
        """
        match node:
            case Binding(target=target, value=value):
                return self._resolve_binding(target, value, node, env, errors)
            case FunctionDef(params=params, body=body):
                final_child = self._resolve_function(params, body, env, errors)
                return env.with_child(final_child)
            case InlineFunctionDef(params=params, body=body):
                final_child = self._resolve_function(params, [body], env, errors)
                return env.with_child(final_child)
            case ForLoop(variable=variable, iterable=iterable, body=body):
                self._resolve_node(iterable, env, errors)
                child = env.child()
                child = self._define_checked(variable.name, variable.position, node, child, env, errors)
                final_child = self._resolve_body(body, child, errors)
                return env.with_child(final_child)
            case IfElse(branches=branches, else_body=else_body):
                for branch in branches:
                    final_child = self._resolve_branch(branch, env, errors)
                    env = env.with_child(final_child)
                if else_body:
                    child = env.child()
                    final_child = self._resolve_body(else_body, child, errors)
                    env = env.with_child(final_child)
                return env
            case Identifier(name=name):
                if env.lookup(name) is None:
                    errors.append(
                        UndefinedVariableError(
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
        """Resolve a ``Binding`` node.

        Checks for duplicate and shadowed names, then registers the
        binding.  For function values the name is registered **before**
        walking the body (enabling self-recursion); for all other values
        the expression is walked first (preventing ``x := x + 1``).
        """
        has_error = self._check_binding(target.name, target.position, env, errors)
        is_function = isinstance(value, FunctionDef | InlineFunctionDef)
        if is_function and not has_error:
            env = env.with_binding(target.name, node)
        env = self._resolve_node(value, env, errors)
        if not is_function and not has_error:
            env = env.with_binding(target.name, node)
        return env

    def _resolve_function(
        self,
        params: list[TypedParam],
        body: list[ASTNode],
        env: Environment[ASTNode],
        errors: list[ResolveError],
    ) -> Environment[ASTNode]:
        """Resolve a function definition (block or inline).

        Creates a child scope, defines each parameter (checking for
        duplicates among the parameters and shadowing against the
        enclosing scope), then walks the function body.  Returns the
        final child environment.
        """
        child = env.child()
        for param in params:
            child = self._define_checked(param.name.name, param.name.position, param.name, child, env, errors)
        return self._resolve_body(body, child, errors)

    def _resolve_branch(
        self,
        branch: ConditionBranch,
        env: Environment[ASTNode],
        errors: list[ResolveError],
    ) -> Environment[ASTNode]:
        """Resolve a single ``if`` or ``elif`` branch.

        The condition is resolved in the current scope.  The branch
        body gets its own child scope so bindings inside the branch
        do not leak out.  Returns the final child environment.
        """
        self._resolve_node(branch.condition, env, errors)
        child = env.child()
        return self._resolve_body(branch.body, child, errors)

    def _resolve_body(
        self,
        body: list[ASTNode],
        env: Environment[ASTNode],
        errors: list[ResolveError],
    ) -> Environment[ASTNode]:
        """Resolve a sequence of statements, threading the environment.

        Each statement may add bindings (via ``Binding`` nodes), so the
        environment is updated after each one and passed to the next.
        """
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
        """Check whether *name* can be legally bound in *env*.

        Reports a ``DUPLICATE_BINDING`` error if *name* already exists
        in the current scope, or a ``SHADOWED_BINDING`` error if it
        exists in any ancestor scope.  Returns ``True`` if a conflict
        was found.
        """
        if env.contains(name):
            errors.append(
                DuplicateBindingError(
                    position=position,
                    name=name,
                )
            )
            return True
        if env.lookup(name) is not None:
            errors.append(
                ShadowedBindingError(
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
        """Define *name* in *env* after checking for conflicts.

        Used for function parameters and loop variables where the
        binding lives in a child scope but must be checked against
        both the child (for duplicate params) and the parent chain
        (for shadowing).
        """
        if env.contains(name):
            errors.append(
                DuplicateBindingError(
                    position=position,
                    name=name,
                )
            )
            return env
        if parent_env.lookup(name) is not None:
            errors.append(
                ShadowedBindingError(
                    position=position,
                    name=name,
                )
            )
            return env
        return env.with_binding(name, node)
