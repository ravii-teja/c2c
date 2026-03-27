from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum


class SourceType(StrEnum):
    DATABASE = "database"
    FILE_SYSTEM = "file_system"
    OBJECT_STORAGE = "object_storage"
    SAAS = "saas"
    DOCUMENT_STORE = "document_store"
    API = "api"


class AssetType(StrEnum):
    TABLE = "table"
    VIEW = "view"
    FILE = "file"
    DIRECTORY = "directory"
    DOCUMENT = "document"
    COLLECTION = "collection"
    ENDPOINT = "endpoint"
    STREAM = "stream"


class FieldType(StrEnum):
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"
    JSON = "json"
    ARRAY = "array"
    UNKNOWN = "unknown"


class AssetCapability(StrEnum):
    STRUCTURED_QUERY = "structured_query"
    CONTENT_RETRIEVAL = "content_retrieval"
    INCREMENTAL_DISCOVERY = "incremental_discovery"
    LINEAGE_HINTS = "lineage_hints"
    POLICY_PROPAGATION = "policy_propagation"
    ROW_LEVEL_FILTERING = "row_level_filtering"
    FRESHNESS_METADATA = "freshness_metadata"


class SensitivityClass(StrEnum):
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"


@dataclass(slots=True)
class SourceDefinition:
    source_id: str
    name: str
    source_type: SourceType
    connection_ref: str
    description: str = ""
    owner: str | None = None
    tags: list[str] = field(default_factory=list)


@dataclass(slots=True)
class Field:
    name: str
    field_type: FieldType = FieldType.UNKNOWN
    description: str = ""
    nullable: bool = True
    tags: list[str] = field(default_factory=list)
    sensitivity: SensitivityClass = SensitivityClass.INTERNAL
    policy_tags: list[str] = field(default_factory=list)


@dataclass(slots=True)
class Asset:
    asset_id: str
    source_id: str
    qualified_name: str
    asset_type: AssetType
    description: str = ""
    fields: list[Field] = field(default_factory=list)
    capabilities: set[AssetCapability] = field(default_factory=set)
    tags: list[str] = field(default_factory=list)
    owners: list[str] = field(default_factory=list)
    sensitivity: SensitivityClass = SensitivityClass.INTERNAL
    policy_tags: list[str] = field(default_factory=list)
    last_seen_at: datetime | None = None


@dataclass(slots=True)
class ProfileStat:
    name: str
    value: str | int | float | bool | None


@dataclass(slots=True)
class AssetProfile:
    asset_id: str
    row_count_estimate: int | None = None
    freshness_hint: str | None = None
    quality_notes: list[str] = field(default_factory=list)
    stats: list[ProfileStat] = field(default_factory=list)


@dataclass(slots=True)
class SampleRecord:
    asset_id: str
    values: dict[str, str | int | float | bool | None]


@dataclass(slots=True)
class ChangeEvent:
    asset_id: str
    change_type: str
    detected_at: datetime
    summary: str


@dataclass(slots=True)
class AssetReference:
    asset_id: str
    qualified_name: str
    source_id: str


@dataclass(slots=True)
class MetadataGraph:
    sources: dict[str, SourceDefinition] = field(default_factory=dict)
    assets: dict[str, Asset] = field(default_factory=dict)
    profiles: dict[str, AssetProfile] = field(default_factory=dict)
    samples: dict[str, list[SampleRecord]] = field(default_factory=dict)
    change_events: list[ChangeEvent] = field(default_factory=list)

    def add_source(self, source: SourceDefinition) -> None:
        self.sources[source.source_id] = source

    def add_asset(self, asset: Asset) -> None:
        self.assets[asset.asset_id] = asset

    def add_profile(self, profile: AssetProfile) -> None:
        self.profiles[profile.asset_id] = profile

    def add_samples(self, asset_id: str, samples: list[SampleRecord]) -> None:
        self.samples[asset_id] = samples

    def add_change_event(self, event: ChangeEvent) -> None:
        self.change_events.append(event)
