from __future__ import annotations

import json
from pathlib import Path

from models import SemanticLayerDraft
from serialization import to_jsonable


class SemanticLayerRepository:
    """Persist semantic-layer drafts as JSON artifacts."""

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def save(self, draft: SemanticLayerDraft) -> Path:
        path = self.root / f"{draft.version}.json"
        path.write_text(json.dumps(to_jsonable(draft), indent=2, sort_keys=True), encoding="utf-8")
        return path

    def load(self, version: str) -> SemanticLayerDraft:
        path = self.root / f"{version}.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        return SemanticLayerDraft(**payload)
