from __future__ import annotations

from ..base_node import BaseNode


class ChesedNode(BaseNode):
    name = "Chesed"
    symbolic_role = "expansion, generosity"
    system_role = "opportunity expansion / broad solution search"

    def process(self, state):
        expanded = list(state.filtered_candidates or state.candidates)
        expanded.append({"strategy": "hybrid_expansion", "score": 0.66})
        state.candidates = expanded
        state.node_outputs[self.name] = {
            "expanded_candidate_count": len(state.candidates),
        }
        return state
