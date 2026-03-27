from pydantic import BaseModel

from spud.core.position import Position
from spud.stage_six.node_type import NodeType


class ASTNode(BaseModel, frozen=True):
    node_type: NodeType
    position: Position
