from __future__ import annotations

import json

from config import SourceRunConfig, ExecutorConfig
from models import SourceType
from workflows import run_bigquery_workflow, run_postgres_workflow


def test_run_postgres_workflow_generates_artifacts(tmp_path) -> None:
    config = SourceRunConfig(
        source_id="pg-test",
        source_name="PG Test",
        source_type=SourceType.DATABASE,
        connection_ref="postgresql://warehouse",
        artifact_root=str(tmp_path / "artifacts"),
        semantic_version="draft-pg-test",
        executor=ExecutorConfig(
            kind="dbapi",
            module="tests.fake_dbapi_module",
            kwargs={"dsn": "postgresql://warehouse"},
        ),
    )

    result = run_postgres_workflow(config)
    summary = json.loads(result.run_summary_path.read_text(encoding="utf-8"))

    assert result.asset_count == 1
    assert result.metric_count == 1
    assert result.metadata_path.exists()
    assert result.contract_path.exists()
    assert summary["source_details"]["kind"] == "postgres"


def test_run_bigquery_workflow_generates_artifacts(tmp_path) -> None:
    config = SourceRunConfig(
        source_id="bq-test",
        source_name="BQ Test",
        source_type=SourceType.DATABASE,
        connection_ref="bigquery://project",
        artifact_root=str(tmp_path / "artifacts"),
        semantic_version="draft-bq-test",
        executor=ExecutorConfig(
            kind="bigquery_client",
            module="tests.fake_bigquery_module",
        ),
    )

    result = run_bigquery_workflow(config)
    summary = json.loads(result.run_summary_path.read_text(encoding="utf-8"))

    assert result.asset_count == 1
    assert result.metric_count == 1
    assert result.metadata_path.exists()
    assert result.contract_path.exists()
    assert summary["source_details"]["kind"] == "bigquery"
