from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class TreeState:
    run_id: str
    user_input: str
    domain: Optional[str] = None
    objective: Optional[str] = None
    task_type: Optional[str] = None

    hypotheses: List[Dict[str, Any]] = field(default_factory=list)
    structured_plan: Dict[str, Any] = field(default_factory=dict)
    candidates: List[Dict[str, Any]] = field(default_factory=list)
    filtered_candidates: List[Dict[str, Any]] = field(default_factory=list)
    selected_strategy: Dict[str, Any] = field(default_factory=dict)

    confidence: float = 0.0
    risk_score: float = 0.0
    novelty_score: float = 0.0
    compliance_passed: bool = True

    route_taken: List[str] = field(default_factory=list)
    node_outputs: Dict[str, Any] = field(default_factory=dict)
    explanation: Optional[str] = None
    final_output: Optional[Dict[str, Any]] = None

    memory_hits: List[Dict[str, Any]] = field(default_factory=list)
    memory: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
