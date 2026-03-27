from __future__ import annotations

import time
from pathlib import Path

from connectors.files import FileSystemConnector
from discovery import ConnectorRunner, SchemaSnapshotRepository
from models import SourceDefinition, SourceType
from org_context import OrganizationContextLoader

from .common import WorkflowResult, execute_semantic_workflow


def run_local_filesystem_workflow(
    *,
    root_path: str,
    artifact_root: str,
    source_id: str = "local-filesystem",
    source_name: str = "Local Filesystem Source",
    semantic_version: str = "draft-v1",
    context_root: str | None = None,
    include_extensions: set[str] | None = None,
    max_files: int = 500,
) -> WorkflowResult:
    resolved_root = Path(root_path).resolve()
    source = SourceDefinition(
        source_id=source_id,
        name=source_name,
        source_type=SourceType.FILE_SYSTEM,
        connection_ref=str(resolved_root),
        description="Local folder scan for documents, tables, and semi-structured files.",
    )

    connector = FileSystemConnector(
        source,
        include_extensions=include_extensions,
        max_files=max_files,
    )
    runner = ConnectorRunner(SchemaSnapshotRepository(Path(artifact_root) / "schema"))
    discovery_started = time.time()
    discovery_result = runner.run(connector)
    discovery_elapsed = round(time.time() - discovery_started, 6)
    organization_context = OrganizationContextLoader().load(context_root) if context_root else None

    return execute_semantic_workflow(
        discovery_result=discovery_result,
        artifact_root=artifact_root,
        source_id=source_id,
        semantic_version=semantic_version,
        source_details={
            "kind": "local_filesystem",
            "root_path": str(resolved_root),
            "include_extensions": sorted(include_extensions or connector.include_extensions),
            "max_files": max_files,
        },
        timings={"discovery_seconds": discovery_elapsed},
        organization_context=organization_context,
    )
