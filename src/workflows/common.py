from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path

from artifacts import ArtifactLayout, ensure_artifact_layout
from discovery import MetadataGraphRepository
from discovery.runner import DiscoveryRunResult
from org_context import OrganizationContextBundle
from semantic_layer import (
    SemanticContractGenerator,
    SemanticContractRepository,
    SemanticLayerRepository,
    SemanticSynthesizer,
)


@dataclass(slots=True)
class WorkflowResult:
    asset_count: int
    entity_count: int
    metric_count: int
    drift_event_count: int
    artifact_layout: ArtifactLayout
    metadata_path: Path
    semantic_path: Path
    contract_path: Path
    run_summary_path: Path


def execute_semantic_workflow(
    *,
    discovery_result: DiscoveryRunResult,
    artifact_root: str,
    source_id: str,
    semantic_version: str,
    source_details: dict[str, object],
    timings: dict[str, float] | None = None,
    organization_context: OrganizationContextBundle | None = None,
) -> WorkflowResult:
    layout = ensure_artifact_layout(artifact_root)
    started_at = time.time()

    # This is the common "discovery -> semantics -> contracts -> artifacts" path
    # shared by local and database-backed workflows.
    semantic_layer = SemanticSynthesizer().synthesize(
        discovery_result.graph,
        version=semantic_version,
        organization_context=organization_context,
    )
    contract_bundle = SemanticContractGenerator().generate(
        semantic_layer,
        organization_context=organization_context,
    )
    metadata_path = MetadataGraphRepository(layout.metadata_dir).save(
        discovery_result.graph,
        name=f"{source_id}-metadata-graph",
    )
    semantic_path = SemanticLayerRepository(layout.semantic_dir).save(semantic_layer)
    contract_path = SemanticContractRepository(layout.semantic_dir).save(contract_bundle)
    completed_at = time.time()

    # The run summary is the lightweight operational trace for a workflow run.
    run_summary_path = layout.runs_dir / f"{source_id}-latest.json"
    run_summary_path.write_text(
        json.dumps(
            {
                "source_id": source_id,
                "source_details": source_details,
                "asset_count": len(discovery_result.graph.assets),
                "entity_count": len(semantic_layer.entities),
                "metric_count": len(semantic_layer.metrics),
                "drift_event_count": discovery_result.drift_event_count,
                "snapshot_saved": discovery_result.snapshot_saved,
                "schema_snapshot_path": (
                    str(discovery_result.schema_snapshot_path)
                    if discovery_result.schema_snapshot_path is not None
                    else None
                ),
                "metadata_path": str(metadata_path),
                "semantic_path": str(semantic_path),
                "contract_path": str(contract_path),
                "timings": {
                    **(timings or {}),
                    "semantic_and_persistence_seconds": round(completed_at - started_at, 6),
                },
            },
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )

    return WorkflowResult(
        asset_count=len(discovery_result.graph.assets),
        entity_count=len(semantic_layer.entities),
        metric_count=len(semantic_layer.metrics),
        drift_event_count=discovery_result.drift_event_count,
        artifact_layout=layout,
        metadata_path=metadata_path,
        semantic_path=semantic_path,
        contract_path=contract_path,
        run_summary_path=run_summary_path,
    )
