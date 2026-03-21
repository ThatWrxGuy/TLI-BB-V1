from __future__ import annotations

from .tree_state import TreeState


class TreeRouter:
    def select_next(self, paths, state: TreeState):
        if not paths:
            return None

        scored = []
        for path in paths:
            score = self._score(path, state)
            scored.append((score, path))

        scored.sort(key=lambda item: item[0], reverse=True)
        return scored[0][1]

    def _score(self, path, state: TreeState) -> float:
        score = 0.5

        if path.to_node == "Gevurah" and state.risk_score >= 0.4:
            score += 0.4
        if path.to_node == "Chokmah" and not state.hypotheses:
            score += 0.3
        if path.to_node == "Binah" and bool(state.hypotheses):
            score += 0.3
        if path.to_node == "Chesed" and not state.filtered_candidates:
            score += 0.25
        if path.to_node == "Tiferet" and (state.filtered_candidates or state.structured_plan):
            score += 0.35
        if path.to_node == "Hod" and bool(state.selected_strategy):
            score += 0.3
        if path.to_node == "Yesod" and (state.final_output is not None or state.explanation):
            score += 0.2
        if path.to_node == "Malkuth" and state.final_output is not None:
            score += 0.5

        loop_penalty = 0.1 * state.route_taken.count(path.to_node)
        return score - loop_penalty
