from __future__ import annotations

from .executor import TreeExecutor
from .memory_store import InMemoryTreeStore
from .metrics import TreeMetrics
from .node_registry import NodeRegistry
from .path_registry import Path, PathRegistry
from .router import TreeRouter
from .nodes.keter import KeterNode
from .nodes.chokmah import ChokmahNode
from .nodes.binah import BinahNode
from .nodes.chesed import ChesedNode
from .nodes.gevurah import GevurahNode
from .nodes.tiferet import TiferetNode
from .nodes.netzach import NetzachNode
from .nodes.hod import HodNode
from .nodes.yesod import YesodNode
from .nodes.malkuth import MalkuthNode


def build_tree() -> TreeExecutor:
    node_registry = NodeRegistry()
    path_registry = PathRegistry()

    for node in [
        KeterNode(),
        ChokmahNode(),
        BinahNode(),
        ChesedNode(),
        GevurahNode(),
        TiferetNode(),
        NetzachNode(),
        HodNode(),
        YesodNode(),
        MalkuthNode(),
    ]:
        node_registry.register(node)

    # 22 canonical Tree paths
    paths = [
        Path("P1", "Keter", "Chokmah", lambda s: True, description="Objective to hypothesis generation"),
        Path("P2", "Keter", "Binah", lambda s: len(s.user_input.split()) < 6, description="Direct structuring for clear requests"),
        Path("P3", "Chokmah", "Binah", lambda s: True, description="Formalize generated hypotheses"),
        Path("P4", "Chokmah", "Chesed", lambda s: len(s.hypotheses) > 2, description="Expand opportunity space"),
        Path("P5", "Binah", "Gevurah", lambda s: True, description="Run governance validation"),
        Path("P6", "Chesed", "Tiferet", lambda s: True, description="Fold exploration into synthesis"),
        Path("P7", "Gevurah", "Tiferet", lambda s: s.compliance_passed, description="Send viable options to synthesis"),
        Path("P8", "Binah", "Tiferet", lambda s: bool(s.structured_plan) and not s.candidates, description="Shortcut for structured tasks"),
        Path("P9", "Tiferet", "Netzach", lambda s: bool(s.selected_strategy), description="Optimize chosen strategy"),
        Path("P10", "Tiferet", "Hod", lambda s: bool(s.selected_strategy), description="Explain synthesized decision"),
        Path("P11", "Tiferet", "Yesod", lambda s: bool(s.selected_strategy), description="Persist selected decision"),
        Path("P12", "Chesed", "Netzach", lambda s: len(s.candidates) > 0, description="Direct high-upside continuation"),
        Path("P13", "Gevurah", "Hod", lambda s: not s.compliance_passed, description="Communicate blocked output"),
        Path("P14", "Netzach", "Hod", lambda s: bool(s.selected_strategy), description="Explain optimized route"),
        Path("P15", "Netzach", "Yesod", lambda s: bool(s.selected_strategy), description="Persist optimization result"),
        Path("P16", "Hod", "Yesod", lambda s: bool(s.explanation), description="Store explanation trace"),
        Path("P17", "Yesod", "Malkuth", lambda s: s.final_output is not None, description="Manifest final output"),
        Path("P18", "Hod", "Malkuth", lambda s: s.final_output is not None, description="Direct presentation path"),
        Path("P19", "Netzach", "Malkuth", lambda s: s.final_output is not None and s.risk_score < 0.2, description="Fast low-risk execution"),
        Path("P20", "Gevurah", "Chesed", lambda s: s.compliance_passed and not s.filtered_candidates and len(s.candidates) > 0, description="Re-expand after over-pruning"),
        Path("P21", "Hod", "Tiferet", lambda s: bool(s.explanation) and not s.final_output, description="Resynthesize if explanation reveals gaps"),
        Path("P22", "Yesod", "Tiferet", lambda s: len(s.memory_hits) > 0 and not s.selected_strategy, description="Memory-guided refinement"),
    ]
    for path in paths:
        path_registry.register(path)

    router = TreeRouter()
    return TreeExecutor(
        node_registry=node_registry,
        path_registry=path_registry,
        router=router,
        memory_store=InMemoryTreeStore(),
        metrics=TreeMetrics(),
    )
