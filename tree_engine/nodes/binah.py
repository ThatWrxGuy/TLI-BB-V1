from __future__ import annotations

from ..base_node import BaseNode


class BinahNode(BaseNode):
    name = "Binah"
    symbolic_role = "structure, understanding"
    system_role = "formalization / schema construction / decomposition"

    def process(self, state):
        state.structured_plan = {
            "task_type": state.task_type,
            "steps": [
                "understand_request",
                "evaluate_options",
                "apply_governance",
                "synthesize_response",
            ],
            "source_hypotheses": [h["hypothesis"] for h in state.hypotheses],
        }
        state.node_outputs[self.name] = state.structured_plan
        return state
