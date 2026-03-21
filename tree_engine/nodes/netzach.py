from __future__ import annotations

from ..base_node import BaseNode


class NetzachNode(BaseNode):
    name = "Netzach"
    symbolic_role = "endurance, momentum"
    system_role = "optimization / persistence / strategy continuation"

    def process(self, state):
        if state.selected_strategy:
            boosted = min(0.99, state.selected_strategy.get("score", 0.5) + 0.05)
            state.selected_strategy["score"] = round(boosted, 2)
            state.confidence = round(boosted, 2)
        state.node_outputs[self.name] = {
            "optimized_strategy": state.selected_strategy,
            "confidence": state.confidence,
        }
        return state
