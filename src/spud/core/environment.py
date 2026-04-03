from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class Environment(BaseModel, Generic[T], frozen=True):
    bindings: dict[str, T] = {}
    parent: "Environment[T] | None" = None

    def with_binding(self, name: str, value: T) -> "Environment[T]":
        return self.model_copy(update={"bindings": {**self.bindings, name: value}})

    def child(self) -> "Environment[T]":
        return Environment(parent=self)

    def lookup(self, name: str) -> T | None:
        if name in self.bindings:
            return self.bindings[name]
        if self.parent is not None:
            return self.parent.lookup(name)
        return None

    def contains(self, name: str) -> bool:
        return name in self.bindings
