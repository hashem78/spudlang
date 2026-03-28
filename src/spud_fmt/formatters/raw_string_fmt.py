from spud.stage_six.ast_node import ASTNode
from spud.stage_six.raw_string_literal import RawStringLiteral


class RawStringFormatter:
    def format(self, node: ASTNode, depth: int) -> str:
        assert isinstance(node, RawStringLiteral)
        return f"`{node.value}`"
