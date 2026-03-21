from __future__ import annotations

import uuid
from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from .setup import build_tree
from .tree_state import TreeState

router = APIRouter(prefix="/tree", tags=["tree-of-life"])
executor = build_tree()


class TreeRunRequest(BaseModel):
    input: str
    domain: Optional[str] = None


@router.get("/health")
def tree_health() -> dict:
    return {"status": "ok", "engine": "tree-of-life", "version": "0.1.0"}


@router.post("/run")
def run_tree(payload: TreeRunRequest) -> dict:
    state = TreeState(
        run_id=str(uuid.uuid4()),
        user_input=payload.input,
        domain=payload.domain,
    )
    result = executor.run("Keter", state)
    return {
        "run_id": result.run_id,
        "route": result.route_taken,
        "objective": result.objective,
        "task_type": result.task_type,
        "confidence": result.confidence,
        "risk_score": result.risk_score,
        "final_output": result.final_output,
        "explanation": result.explanation,
        "metrics": result.metadata.get("metrics", {}),
    }
