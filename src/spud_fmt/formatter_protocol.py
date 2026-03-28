from typing import Protocol

from spud.stage_six.ast_node import ASTNode


class FormatterDispatch(Protocol):
    def format_node(self, node: ASTNode, depth: int) -> str: ...


class NodeFormatter(Protocol):
    def format(self, node: ASTNode, depth: int) -> str: ...
