from __future__ import annotations

import json
from pathlib import Path

from connectors.databases import SchemaSnapshot


class SchemaSnapshotRepository:
    """Persist and retrieve schema snapshots per source."""

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def load_latest(self, source_id: str) -> SchemaSnapshot | None:
        path = self.root / f"{source_id}.json"
        if not path.exists():
            return None
        payload = json.loads(path.read_text(encoding="utf-8"))
        return SchemaSnapshot(
            source_id=payload["source_id"],
            captured_at=_parse_datetime(payload["captured_at"]),
            asset_signatures=payload["asset_signatures"],
        )

    def save_latest(self, snapshot: SchemaSnapshot) -> Path:
        path = self.root / f"{snapshot.source_id}.json"
        payload = {
            "source_id": snapshot.source_id,
            "captured_at": snapshot.captured_at.isoformat(),
            "asset_signatures": snapshot.asset_signatures,
        }
        path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        return path


def _parse_datetime(value: str):
    from datetime import datetime

    return datetime.fromisoformat(value)
