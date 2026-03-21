from dataclasses import dataclass
from typing import Callable

from .tree_state import TreeState


@dataclass
class Path:
    path_id: str
    from_node: str
    to_node: str
    condition: Callable[[TreeState], bool]
    routing_mode: str = "hybrid"
    description: str = ""


class PathRegistry:
    def __init__(self):
        self.paths = []

    def register(self, path: Path):
        self.paths.append(path)

    def get_valid_paths(self, current_node: str, state: TreeState):
        return [
            path for path in self.paths
            if path.from_node == current_node and path.condition(state)
        ]
