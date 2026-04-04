from typing import Literal

from spud.stage_six.ast_node import ASTNode
from spud.stage_six.identifier import Identifier
from spud.stage_six.node_type import NodeType
from spud.stage_six.type_expression import TypeExpression


class ForLoop(ASTNode, frozen=True):
    node_type: Literal[NodeType.FOR_LOOP] = NodeType.FOR_LOOP
    variable: Identifier
    variable_type: TypeExpression
    iterable: ASTNode
    body: list[ASTNode]
