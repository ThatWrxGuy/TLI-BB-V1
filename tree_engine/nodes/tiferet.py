from __future__ import annotations

from ..base_node import BaseNode


class TiferetNode(BaseNode):
    name = "Tiferet"
    symbolic_role = "harmony, balance"
    system_role = "synthesis / decision fusion layer"

    def process(self, state):
        pool = state.filtered_candidates or state.candidates
        if pool:
            selected = sorted(pool, key=lambda item: item.get("score", 0), reverse=True)[0]
            state.selected_strategy = selected
            state.confidence = round(selected.get("score", 0.5), 2)
            state.final_output = {
                "decision": f"Selected {selected['strategy']} strategy",
                "strategy": selected,
                "objective": state.objective,
            }
        state.node_outputs[self.name] = {
            "selected_strategy": state.selected_strategy,
            "confidence": state.confidence,
        }
        return state
