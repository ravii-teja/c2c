from __future__ import annotations

from connectors import ConnectorRegistry
from models import MetadataGraph

from .runner import ConnectorRunner


class DiscoveryService:
    """Build a unified metadata graph from all registered connectors."""

    def __init__(self, registry: ConnectorRegistry, runner: ConnectorRunner | None = None) -> None:
        self.registry = registry
        self.runner = runner or ConnectorRunner()

    def build_graph(self) -> MetadataGraph:
        graph = MetadataGraph()
        for connector in self.registry.list():
            result = self.runner.run(connector)
            for source in result.graph.sources.values():
                graph.add_source(source)
            for asset in result.graph.assets.values():
                graph.add_asset(asset)
            for profile in result.graph.profiles.values():
                graph.add_profile(profile)
            for asset_id, samples in result.graph.samples.items():
                graph.add_samples(asset_id, samples)
            for change_event in result.graph.change_events:
                graph.add_change_event(change_event)
        return graph
