from __future__ import annotations

from ..base_node import BaseNode


class KeterNode(BaseNode):
    name = "Keter"
    symbolic_role = "origin, pure intent"
    system_role = "mission framing / top-level objective selection"

    def process(self, state):
        state.objective = f"Process request: {state.user_input[:80]}"
        text = state.user_input.lower()
        if any(word in text for word in ["predict", "forecast", "estimate"]):
            state.task_type = "predictive"
        elif any(word in text for word in ["build", "create", "design"]):
            state.task_type = "generative"
        elif any(word in text for word in ["risk", "safe", "governance"]):
            state.task_type = "governance"
        else:
            state.task_type = "advisory"
        state.node_outputs[self.name] = {
            "objective": state.objective,
            "task_type": state.task_type,
        }
        return state
