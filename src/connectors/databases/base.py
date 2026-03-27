from __future__ import annotations

from abc import abstractmethod
from datetime import datetime, UTC

from connectors.base import Connector
from models import (
    Asset,
    AssetCapability,
    AssetProfile,
    AssetType,
    ChangeEvent,
    Field,
    FieldType,
    ProfileStat,
    SampleRecord,
)

from .executor import QueryExecutor, Row
from .schema_snapshot import SchemaSnapshot, compare_snapshots, snapshot_from_assets


class DatabaseConnector(Connector):
    """
    Shared foundation for queryable database and warehouse connectors.

    Concrete implementations should focus on connection/auth specifics and
    system catalog queries while inheriting common capability semantics.
    """

    connector_family = "database"

    def __init__(self, source, executor: QueryExecutor) -> None:
        super().__init__(source)
        self.executor = executor

    def list_capabilities(self) -> set[str]:
        return {
            "discover_assets",
            "profile_asset",
            "sample_asset",
            "structured_query",
            "schema_drift_detection",
            "lineage_hints",
            "freshness_metadata",
        }

    def default_asset_capabilities(self) -> set[AssetCapability]:
        return {
            AssetCapability.STRUCTURED_QUERY,
            AssetCapability.INCREMENTAL_DISCOVERY,
            AssetCapability.LINEAGE_HINTS,
            AssetCapability.POLICY_PROPAGATION,
            AssetCapability.ROW_LEVEL_FILTERING,
            AssetCapability.FRESHNESS_METADATA,
        }

    @abstractmethod
    def discover_assets(self) -> list[Asset]:
        """Discover accessible tables, views, schemas, or lake objects."""

    @abstractmethod
    def profile_asset(self, asset: Asset) -> AssetProfile:
        """Profile an asset for row counts, freshness, and quality hints."""

    @abstractmethod
    def sample_asset(self, asset: Asset, limit: int = 5) -> list[SampleRecord]:
        """Return representative sample rows."""

    @abstractmethod
    def detect_changes(self) -> list[ChangeEvent]:
        """Return detected schema or asset changes."""

    def _build_asset(
        self,
        *,
        qualified_name: str,
        asset_type: AssetType,
        fields: list[Field],
        description: str = "",
        tags: list[str] | None = None,
    ) -> Asset:
        return Asset(
            asset_id=f"{self.source.source_id}:{qualified_name}",
            source_id=self.source.source_id,
            qualified_name=qualified_name,
            asset_type=asset_type,
            description=description,
            fields=fields,
            capabilities=self.default_asset_capabilities(),
            tags=tags or [],
            last_seen_at=datetime.now(UTC),
        )

    def _profile_from_row(
        self,
        *,
        asset_id: str,
        row_count: int | None = None,
        freshness_hint: str | None = None,
        extra_stats: dict[str, str | int | float | bool | None] | None = None,
    ) -> AssetProfile:
        stats = [
            ProfileStat(name=name, value=value)
            for name, value in sorted((extra_stats or {}).items())
        ]
        return AssetProfile(
            asset_id=asset_id,
            row_count_estimate=row_count,
            freshness_hint=freshness_hint,
            stats=stats,
        )

    def _sample_records_from_rows(self, asset_id: str, rows: list[Row]) -> list[SampleRecord]:
        return [SampleRecord(asset_id=asset_id, values=row) for row in rows]

    def build_schema_snapshot(self, assets: list[Asset]) -> SchemaSnapshot:
        return snapshot_from_assets(self.source.source_id, assets)

    def diff_schema_snapshots(
        self, previous: SchemaSnapshot, current: SchemaSnapshot
    ) -> list[ChangeEvent]:
        return compare_snapshots(previous, current)

    def _candidate_freshness_fields(self, fields: list[Field]) -> list[str]:
        ranked_names = []
        priority_tokens = (
            "updated_at",
            "modified_at",
            "last_updated_at",
            "last_modified_at",
            "event_timestamp",
            "event_time",
            "timestamp",
            "created_at",
        )
        existing = {field.name.lower(): field.name for field in fields}
        for token in priority_tokens:
            if token in existing:
                ranked_names.append(existing[token])
        return ranked_names

    def _map_field_type(self, raw_type: str | None) -> FieldType:
        lowered = (raw_type or "").lower()
        if lowered in {"character varying", "varchar", "text", "string"}:
            return FieldType.STRING
        if lowered in {"integer", "bigint", "smallint", "int64", "int", "numeric_integer"}:
            return FieldType.INTEGER
        if lowered in {"numeric", "decimal", "double precision", "float", "float64", "real"}:
            return FieldType.FLOAT
        if lowered in {"boolean", "bool"}:
            return FieldType.BOOLEAN
        if lowered == "date":
            return FieldType.DATE
        if lowered in {"timestamp", "timestamp without time zone", "timestamp with time zone", "datetime"}:
            return FieldType.DATETIME
        if lowered in {"json", "jsonb", "record"}:
            return FieldType.JSON
        if lowered.startswith("array") or lowered.endswith("[]"):
            return FieldType.ARRAY
        return FieldType.UNKNOWN
