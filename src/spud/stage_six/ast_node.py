from pydantic import BaseModel

from spud.stage_six.node_type import NodeType


class ASTNode(BaseModel, frozen=True):
    node_type: NodeType
