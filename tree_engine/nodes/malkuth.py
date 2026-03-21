from __future__ import annotations

from ..base_node import BaseNode


class MalkuthNode(BaseNode):
    name = "Malkuth"
    symbolic_role = "manifestation, realized form"
    system_role = "final output / action / externalized result"

    def process(self, state):
        if state.final_output is None:
            state.final_output = {"decision": "no_output_generated"}
        state.node_outputs[self.name] = state.final_output
        return state
