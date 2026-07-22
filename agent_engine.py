"""Thin compatibility exports for the Phase 1 engine."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from textile_foundry.graph import build_graph, run_request

__all__ = ["build_graph", "run_request"]
