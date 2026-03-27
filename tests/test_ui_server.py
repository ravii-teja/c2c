from __future__ import annotations

import json

from ui.server import _scan_payload


def test_ui_scan_payload_returns_semantic_summary(tmp_path) -> None:
    root = tmp_path / "workspace"
    root.mkdir()
    (root / "orders.csv").write_text("order_id,customer_id,revenue\n1,100,25\n", encoding="utf-8")
    artifact_root = tmp_path / "artifacts"

    payload = _scan_payload(
        {
            "root_path": str(root),
            "artifact_root": str(artifact_root),
            "extensions": ["csv"],
            "max_files": 10,
        }
    )

    assert payload["summary"]["asset_count"] == 1
    assert payload["entities"]
    assert payload["assets"][0]["qualified_name"] == "orders.csv"
