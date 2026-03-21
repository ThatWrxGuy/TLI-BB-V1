from __future__ import annotations

from ..base_node import BaseNode


class GevurahNode(BaseNode):
    name = "Gevurah"
    symbolic_role = "constraint, severity"
    system_role = "governance / risk filter / hard-boundary enforcement"

    def process(self, state):
        text = state.user_input.lower()
        risky = any(word in text for word in ["guarantee", "certain", "always", "bypass"])
        state.risk_score = 0.65 if risky else 0.18
        threshold = 0.70 if risky else 0.60
        state.filtered_candidates = [c for c in state.candidates if c.get("score", 0) >= threshold]
        state.compliance_passed = not risky or bool(state.filtered_candidates)
        state.node_outputs[self.name] = {
            "risk_score": state.risk_score,
            "compliance_passed": state.compliance_passed,
            "filtered_candidate_count": len(state.filtered_candidates),
        }
        return state
