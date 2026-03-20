from __future__ import annotations

from .tree_state import TreeState


class TreeExecutor:
    def __init__(self, node_registry, path_registry, router, memory_store=None, metrics=None):
        self.node_registry = node_registry
        self.path_registry = path_registry
        self.router = router
        self.memory_store = memory_store
        self.metrics = metrics

    def run(self, start_node: str, state: TreeState, max_steps: int = 20) -> TreeState:
        current = start_node
        steps = 0

        while current and steps < max_steps:
            node = self.node_registry.get(current)
            if node is None:
                break

            state = node.process(state)
            state.route_taken.append(current)
            steps += 1

            valid_paths = self.path_registry.get_valid_paths(current, state)
            next_path = self.router.select_next(valid_paths, state)
            current = next_path.to_node if next_path else None

        if self.memory_store:
            self.memory_store.save(state)
        if self.metrics:
            state.metadata["metrics"] = self.metrics.summarize(state)
        return state
