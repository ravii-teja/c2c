from __future__ import annotations

from abc import ABC, abstractmethod

from models import Asset, AssetProfile, ChangeEvent, SampleRecord, SourceDefinition


class Connector(ABC):
    """Base contract for all source connectors."""

    def __init__(self, source: SourceDefinition) -> None:
        self.source = source

    @abstractmethod
    def discover_assets(self) -> list[Asset]:
        """Return assets accessible for this source."""

    @abstractmethod
    def profile_asset(self, asset: Asset) -> AssetProfile:
        """Return lightweight profiling data for an asset."""

    @abstractmethod
    def sample_asset(self, asset: Asset, limit: int = 5) -> list[SampleRecord]:
        """Return representative sample records for discovery and synthesis."""

    @abstractmethod
    def detect_changes(self) -> list[ChangeEvent]:
        """Return drift or schema change events."""

    @abstractmethod
    def list_capabilities(self) -> set[str]:
        """Return connector-level capability strings."""
