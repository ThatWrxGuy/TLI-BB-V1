from __future__ import annotations

from ..base_node import BaseNode


class HodNode(BaseNode):
    name = "Hod"
    symbolic_role = "language, signal"
    system_role = "representation / explanation / communication formatting"

    def process(self, state):
        if state.compliance_passed and state.final_output:
            state.explanation = (
                f"Processed as {state.task_type} task using "
                f"{state.selected_strategy.get('strategy', 'unknown')} strategy "
                f"with confidence {state.confidence:.2f}."
            )
        else:
            state.explanation = "Output constrained by governance and requires review."
            if state.final_output is None:
                state.final_output = {
                    "decision": "manual_review",
                    "reason": "governance_block_or_missing_strategy",
                }
        state.node_outputs[self.name] = {
            "explanation": state.explanation,
        }
        return state
