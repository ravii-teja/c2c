from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from connectors.base import Connector
from connectors.databases import DatabaseConnector
from models import MetadataGraph

from .snapshot_repository import SchemaSnapshotRepository


@dataclass(slots=True)
class DiscoveryRunResult:
    graph: MetadataGraph
    snapshot_saved: bool
    schema_snapshot_path: Path | None
    drift_event_count: int


class ConnectorRunner:
    """Run discovery, profiling, sampling, and drift comparison for one connector."""

    def __init__(self, snapshot_repository: SchemaSnapshotRepository | None = None) -> None:
        self.snapshot_repository = snapshot_repository

    def run(self, connector: Connector) -> DiscoveryRunResult:
        graph = MetadataGraph()
        graph.add_source(connector.source)

        assets = connector.discover_assets()
        for asset in assets:
            graph.add_asset(asset)
            graph.add_profile(connector.profile_asset(asset))
            graph.add_samples(asset.asset_id, connector.sample_asset(asset))

        snapshot_saved = False
        schema_snapshot_path: Path | None = None
        if isinstance(connector, DatabaseConnector) and self.snapshot_repository is not None:
            current_snapshot = connector.build_schema_snapshot(assets)
            previous_snapshot = self.snapshot_repository.load_latest(connector.source.source_id)
            if previous_snapshot is not None:
                for change_event in connector.diff_schema_snapshots(previous_snapshot, current_snapshot):
                    graph.add_change_event(change_event)
            schema_snapshot_path = self.snapshot_repository.save_latest(current_snapshot)
            snapshot_saved = True

        for change_event in connector.detect_changes():
            graph.add_change_event(change_event)

        return DiscoveryRunResult(
            graph=graph,
            snapshot_saved=snapshot_saved,
            schema_snapshot_path=schema_snapshot_path,
            drift_event_count=len(graph.change_events),
        )
