from typing import Generic, TypeVar

K = TypeVar("K")
V = TypeVar("V")


class TrieNode(Generic[K, V]):
    def __init__(self) -> None:
        self.children: dict[K, TrieNode[K, V]] = {}
        self.value: V | None = None


class Trie(Generic[K, V]):
    def __init__(self) -> None:
        self._root = TrieNode[K, V]()

    @property
    def root(self) -> TrieNode[K, V]:
        return self._root

    def insert(self, sequence: list[K], value: V) -> None:
        node = self._root
        for key in sequence:
            if key not in node.children:
                node.children[key] = TrieNode[K, V]()
            node = node.children[key]
        node.value = value
