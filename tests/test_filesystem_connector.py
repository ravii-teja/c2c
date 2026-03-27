from __future__ import annotations

import json

from connectors.files import FileSystemConnector
from models import SourceDefinition, SourceType


def test_filesystem_connector_discovers_common_local_files(tmp_path) -> None:
    root = tmp_path / "workspace"
    root.mkdir()
    (root / "orders.csv").write_text("order_id,customer_id,revenue\n1,100,25\n", encoding="utf-8")
    (root / "notes.md").write_text("# Notes\nCustomer pipeline update", encoding="utf-8")
    (root / "accounts.json").write_text(
        json.dumps([{"account_id": 1, "email": "a@example.com"}]),
        encoding="utf-8",
    )

    connector = FileSystemConnector(
        SourceDefinition(
            source_id="fs1",
            name="Local Files",
            source_type=SourceType.FILE_SYSTEM,
            connection_ref=str(root),
        )
    )

    assets = connector.discover_assets()
    assert len(assets) == 3
    qualified_names = sorted(asset.qualified_name for asset in assets)
    assert qualified_names == ["accounts.json", "notes.md", "orders.csv"]

    csv_asset = next(asset for asset in assets if asset.qualified_name == "orders.csv")
    profile = connector.profile_asset(csv_asset)
    assert profile.row_count_estimate == 1

    samples = connector.sample_asset(csv_asset, limit=1)
    assert samples[0].values["revenue"] == "25"


def test_filesystem_connector_detects_document_preview(tmp_path) -> None:
    root = tmp_path / "workspace"
    root.mkdir()
    (root / "strategy.txt").write_text("Revenue expansion plan for enterprise accounts", encoding="utf-8")

    connector = FileSystemConnector(
        SourceDefinition(
            source_id="fs2",
            name="Local Files",
            source_type=SourceType.FILE_SYSTEM,
            connection_ref=str(root),
        )
    )

    asset = connector.discover_assets()[0]
    samples = connector.sample_asset(asset, limit=1)
    assert "Revenue expansion plan" in samples[0].values["preview"]
