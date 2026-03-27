from __future__ import annotations

import json

from workflows import run_local_csv_workflow


def test_local_csv_workflow_generates_expected_artifacts(tmp_path) -> None:
    data_dir = tmp_path / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / "orders.csv").write_text(
        "order_id,total_amount\n1,10.5\n2,20.0\n",
        encoding="utf-8",
    )

    result = run_local_csv_workflow(
        csv_root=str(data_dir),
        artifact_root=str(tmp_path / "artifacts"),
        source_id="csv-test",
        semantic_version="draft-csv-test",
    )

    assert result.asset_count == 1
    assert result.entity_count == 1
    assert result.metric_count == 1
    assert result.metadata_path.exists()
    assert result.semantic_path.exists()
    assert result.contract_path.exists()
    assert result.run_summary_path.exists()

    summary = json.loads(result.run_summary_path.read_text(encoding="utf-8"))
    assert summary["source_id"] == "csv-test"
    assert summary["asset_count"] == 1
    assert summary["contract_path"].endswith("draft-csv-test-contracts.json")
