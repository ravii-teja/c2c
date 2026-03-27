from __future__ import annotations

import time
from pathlib import Path

from connectors.files import CsvConnector
from discovery import ConnectorRunner, SchemaSnapshotRepository
from models import SourceDefinition, SourceType
from org_context import OrganizationContextLoader

from .common import WorkflowResult, execute_semantic_workflow

LocalCsvWorkflowResult = WorkflowResult


def run_local_csv_workflow(
    *,
    csv_root: str,
    artifact_root: str,
    source_id: str = "local-csv",
    source_name: str = "Local CSV Source",
    semantic_version: str = "draft-v1",
    context_root: str | None = None,
) -> WorkflowResult:
    source = SourceDefinition(
        source_id=source_id,
        name=source_name,
        source_type=SourceType.FILE_SYSTEM,
        connection_ref=str(Path(csv_root).resolve()),
        description="Local folder of CSV files for discovery and semantic synthesis.",
    )

    connector = CsvConnector(source)
    runner = ConnectorRunner(SchemaSnapshotRepository(Path(artifact_root) / "schema"))
    discovery_started = time.time()
    discovery_result = runner.run(connector)
    discovery_elapsed = round(time.time() - discovery_started, 6)
    organization_context = OrganizationContextLoader().load(context_root) if context_root else None

    workflow_result = execute_semantic_workflow(
        discovery_result=discovery_result,
        artifact_root=artifact_root,
        source_id=source_id,
        semantic_version=semantic_version,
        source_details={
            "kind": "local_csv",
            "csv_root": str(Path(csv_root).resolve()),
        },
        timings={"discovery_seconds": discovery_elapsed},
        organization_context=organization_context,
    )

    return workflow_result
