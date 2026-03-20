from __future__ import annotations

from abc import ABC, abstractmethod

from .tree_state import TreeState


class BaseNode(ABC):
    name: str
    symbolic_role: str = ""
    system_role: str = ""

    @abstractmethod
    def process(self, state: TreeState) -> TreeState:
        raise NotImplementedError

    def metrics(self) -> dict:
        return {"node": self.name}
