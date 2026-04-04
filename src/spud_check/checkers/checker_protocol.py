from typing import Protocol, TypeVar

from spud.core import Environment
from spud.core.types import SpudType
from spud.stage_six import ASTNode
from spud_check.type_errors import TypeError
from spud_check.typed_nodes import TypedNode

T = TypeVar("T", covariant=True)


class INodeChecker(Protocol[T]):
    def check(
        self,
        node: ASTNode,
        env: Environment[SpudType],
        errors: list[TypeError],
    ) -> tuple[T, Environment[SpudType]]: ...


class INodeCheckerDispatch(Protocol):
    def dispatch(
        self,
        node: ASTNode,
        env: Environment[SpudType],
        errors: list[TypeError],
    ) -> tuple[TypedNode, Environment[SpudType]]: ...
