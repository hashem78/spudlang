from __future__ import annotations

from typing import Literal

from spud.stage_six.ast_node import ASTNode
from spud.stage_six.node_type import NodeType
from spud.stage_six.parse_error import ParseError


class Program(ASTNode, frozen=True):
    node_type: Literal[NodeType.PROGRAM] = NodeType.PROGRAM
    body: list[ASTNode]
    errors: list[ParseError] = []
