from tree_engine.setup import build_tree
from tree_engine.tree_state import TreeState


def test_tree_engine_smoke():
    executor = build_tree()
    state = TreeState(run_id="test-1", user_input="Design a safe strategy for an ML experiment")
    result = executor.run("Keter", state)

    assert result.route_taken[0] == "Keter"
    assert result.final_output is not None
    assert "metrics" in result.metadata
