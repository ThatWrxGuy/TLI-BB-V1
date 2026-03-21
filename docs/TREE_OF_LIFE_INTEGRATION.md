# Busy Bee Tree-of-Life Integration Package

This package preserves the existing Busy Bee repository and adds a new `tree_engine/` folder for a Tree-of-Life-inspired execution model.

## What was added

- `tree_engine/` package with 10 nodes and 22 paths
- FastAPI router at `tree_engine/api.py`
- smoke test at `tests/test_tree_engine.py`

## Suggested integration

In `app/api/main.py`, add:

```python
from tree_engine.api import router as tree_router
app.include_router(tree_router)
```

That exposes:
- `GET /tree/health`
- `POST /tree/run`

## Why this approach

The existing repo stays intact. The Tree engine sits on top as a new experimental orchestration layer, so you can evolve the architecture without rewriting the production code immediately.
