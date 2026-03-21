from __future__ import annotations

from collections import Counter
from typing import Dict

from .tree_state import TreeState


class TreeMetrics:
    def summarize(self, state: TreeState) -> Dict:
        path_counts = Counter(state.route_taken)
        return {
            "route_length": len(state.route_taken),
            "path_counts": dict(path_counts),
            "confidence": state.confidence,
            "risk_score": state.risk_score,
            "compliance_passed": state.compliance_passed,
        }
