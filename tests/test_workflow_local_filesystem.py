from __future__ import annotations

import json

from workflows import run_local_filesystem_workflow


def test_local_filesystem_workflow_builds_semantic_outputs(tmp_path) -> None:
    root = tmp_path / "workspace"
    root.mkdir()
    (root / "orders.csv").write_text("order_id,customer_id,total_amount\n1,100,25\n", encoding="utf-8")
    (root / "customers.csv").write_text("id,email\n100,a@example.com\n", encoding="utf-8")
    artifact_root = tmp_path / "artifacts"

    result = run_local_filesystem_workflow(
        root_path=str(root),
        artifact_root=str(artifact_root),
        max_files=20,
    )

    assert result.asset_count == 2
    payload = json.loads(result.contract_path.read_text(encoding="utf-8"))
    assert payload["entities"]
    assert payload["metrics"]
    assert payload["relationships"]
