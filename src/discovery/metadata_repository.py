from __future__ import annotations

import json
from pathlib import Path

from models import MetadataGraph
from serialization import to_jsonable


class MetadataGraphRepository:
    """Persist metadata graphs as JSON artifacts."""

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def save(self, graph: MetadataGraph, name: str = "metadata-graph") -> Path:
        path = self.root / f"{name}.json"
        path.write_text(json.dumps(to_jsonable(graph), indent=2, sort_keys=True), encoding="utf-8")
        return path
