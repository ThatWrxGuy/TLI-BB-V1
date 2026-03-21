from __future__ import annotations

from collections import deque
from typing import Deque, Dict, List

from .tree_state import TreeState


class InMemoryTreeStore:
    def __init__(self, max_runs: int = 100):
        self._runs: Deque[dict] = deque(maxlen=max_runs)

    def save(self, state: TreeState) -> None:
        self._runs.append({
            "run_id": state.run_id,
            "user_input": state.user_input,
            "objective": state.objective,
            "route": list(state.route_taken),
            "final_output": state.final_output,
            "confidence": state.confidence,
        })

    def recent(self, limit: int = 5) -> List[Dict]:
        return list(self._runs)[-limit:]
