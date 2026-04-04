from __future__ import annotations

from typing import Literal

from spud.core.resolve_errors.resolve_error import ResolveError
from spud.stage_six.ast_node import ASTNode
from spud.stage_six.node_type import NodeType
from spud.stage_six.parse_errors.parse_error import ParseError


class Program(ASTNode, frozen=True):
    node_type: Literal[NodeType.PROGRAM] = NodeType.PROGRAM
    body: list[ASTNode]
    errors: list[ParseError | ResolveError] = []
