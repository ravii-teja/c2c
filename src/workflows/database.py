from __future__ import annotations

import time

from artifacts import ensure_artifact_layout
from config import SourceRunConfig
from connectors.databases import BigQueryConnector, PostgresConnector
from discovery import ConnectorRunner, SchemaSnapshotRepository
from integrations import build_executor_from_config
from org_context import OrganizationContextLoader

from .common import WorkflowResult, execute_semantic_workflow


def run_postgres_workflow(config: SourceRunConfig) -> WorkflowResult:
    if config.executor is None:
        raise ValueError("Postgres workflow requires executor configuration.")

    executor = build_executor_from_config(config.executor)
    connector = PostgresConnector(config.to_source_definition(), executor=executor)
    layout = ensure_artifact_layout(config.artifact_root)

    discovery_started = time.time()
    discovery_result = ConnectorRunner(SchemaSnapshotRepository(layout.schema_dir)).run(connector)
    discovery_elapsed = round(time.time() - discovery_started, 6)
    organization_context = (
        OrganizationContextLoader().load(config.context_root) if config.context_root else None
    )

    result = execute_semantic_workflow(
        discovery_result=discovery_result,
        artifact_root=config.artifact_root,
        source_id=config.source_id,
        semantic_version=config.semantic_version,
        source_details={
            "kind": "postgres",
            "connection_ref": config.connection_ref,
            "executor_kind": config.executor.kind,
        },
        timings={"discovery_seconds": discovery_elapsed},
        organization_context=organization_context,
    )
    return result


def run_bigquery_workflow(config: SourceRunConfig) -> WorkflowResult:
    if config.executor is None:
        raise ValueError("BigQuery workflow requires executor configuration.")

    executor = build_executor_from_config(config.executor)
    connector = BigQueryConnector(config.to_source_definition(), executor=executor)
    layout = ensure_artifact_layout(config.artifact_root)

    discovery_started = time.time()
    discovery_result = ConnectorRunner(SchemaSnapshotRepository(layout.schema_dir)).run(connector)
    discovery_elapsed = round(time.time() - discovery_started, 6)
    organization_context = (
        OrganizationContextLoader().load(config.context_root) if config.context_root else None
    )

    result = execute_semantic_workflow(
        discovery_result=discovery_result,
        artifact_root=config.artifact_root,
        source_id=config.source_id,
        semantic_version=config.semantic_version,
        source_details={
            "kind": "bigquery",
            "connection_ref": config.connection_ref,
            "executor_kind": config.executor.kind,
        },
        timings={"discovery_seconds": discovery_elapsed},
        organization_context=organization_context,
    )
    return result
