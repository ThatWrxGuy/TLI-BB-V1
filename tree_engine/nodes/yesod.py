from __future__ import annotations

from ..base_node import BaseNode


class YesodNode(BaseNode):
    name = "Yesod"
    symbolic_role = "foundation, mediation"
    system_role = "memory integration / state persistence / execution bridge"

    def process(self, state):
        prior = state.memory.get("last_run")
        if prior:
            state.memory_hits.append(prior)
        state.memory["last_run"] = {
            "objective": state.objective,
            "route": list(state.route_taken),
            "final_output": state.final_output,
        }
        state.node_outputs[self.name] = {
            "memory_hits": len(state.memory_hits),
            "stored": True,
        }
        return state
