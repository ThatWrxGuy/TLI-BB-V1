from __future__ import annotations

from ..base_node import BaseNode


class ChokmahNode(BaseNode):
    name = "Chokmah"
    symbolic_role = "emergence, expansive insight"
    system_role = "hypothesis generation / candidate expansion"

    def process(self, state):
        words = [w.strip(',.?!') for w in state.user_input.split() if w.strip(',.?!')]
        key_terms = words[:5]
        state.hypotheses = [
            {"id": 1, "hypothesis": f"direct_answer::{state.task_type}", "keywords": key_terms},
            {"id": 2, "hypothesis": "structured_breakdown", "keywords": key_terms[:3]},
            {"id": 3, "hypothesis": "risk_adjusted_response", "keywords": key_terms[-3:]},
        ]
        state.candidates = [
            {"strategy": "direct", "score": 0.68},
            {"strategy": "decompose", "score": 0.74},
            {"strategy": "governed", "score": 0.71},
        ]
        state.novelty_score = 0.55
        state.node_outputs[self.name] = {
            "hypotheses": state.hypotheses,
            "candidate_count": len(state.candidates),
        }
        return state
