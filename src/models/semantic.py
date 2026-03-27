from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum

from .metadata import AssetReference, SensitivityClass


class RelationshipKind(StrEnum):
    PRIMARY_FOREIGN_KEY = "primary_foreign_key"
    SOFT_MATCH = "soft_match"
    DOCUMENT_REFERENCE = "document_reference"
    INFERRED_EQUIVALENCE = "inferred_equivalence"


class ContractStatus(StrEnum):
    DRAFT = "draft"
    VALIDATED = "validated"
    PRODUCTION = "production"
    DEPRECATED = "deprecated"


@dataclass(slots=True)
class CanonicalEntity:
    entity_id: str
    name: str
    description: str = ""
    synonyms: list[str] = field(default_factory=list)
    asset_references: list[AssetReference] = field(default_factory=list)
    confidence: float = 0.0


@dataclass(slots=True)
class CanonicalMetric:
    metric_id: str
    name: str
    description: str = ""
    formula_hint: str = ""
    grain: str = ""
    source_assets: list[AssetReference] = field(default_factory=list)
    confidence: float = 0.0


@dataclass(slots=True)
class CandidateMetric:
    metric_name: str
    asset_ref: AssetReference
    confidence: float
    reason: str


@dataclass(slots=True)
class CandidateRelationship:
    left_asset: AssetReference
    right_asset: AssetReference
    relationship_kind: RelationshipKind
    confidence: float
    evidence: str


@dataclass(slots=True)
class SemanticLayerDraft:
    version: str
    entities: list[CanonicalEntity] = field(default_factory=list)
    metrics: list[CanonicalMetric] = field(default_factory=list)
    relationships: list[CandidateRelationship] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


@dataclass(slots=True)
class MetricContract:
    metric_id: str
    name: str
    description: str = ""
    formula_hint: str = ""
    grain: str = ""
    owner: str | None = None
    source_assets: list[AssetReference] = field(default_factory=list)
    synonyms: list[str] = field(default_factory=list)
    confidence: float = 0.0
    status: ContractStatus = ContractStatus.DRAFT
    sensitivity: SensitivityClass = SensitivityClass.INTERNAL
    policy_tags: list[str] = field(default_factory=list)
    validation_notes: list[str] = field(default_factory=list)


@dataclass(slots=True)
class EntityContract:
    entity_id: str
    name: str
    description: str = ""
    owner: str | None = None
    synonyms: list[str] = field(default_factory=list)
    source_assets: list[AssetReference] = field(default_factory=list)
    confidence: float = 0.0
    status: ContractStatus = ContractStatus.DRAFT
    sensitivity: SensitivityClass = SensitivityClass.INTERNAL
    policy_tags: list[str] = field(default_factory=list)


@dataclass(slots=True)
class RelationshipContract:
    relationship_id: str
    left_asset: AssetReference
    right_asset: AssetReference
    relationship_kind: RelationshipKind
    confidence: float = 0.0
    status: ContractStatus = ContractStatus.DRAFT
    sensitivity: SensitivityClass = SensitivityClass.INTERNAL
    policy_tags: list[str] = field(default_factory=list)
    evidence: str = ""
    validation_notes: list[str] = field(default_factory=list)


@dataclass(slots=True)
class SemanticContractBundle:
    version: str
    entities: list[EntityContract] = field(default_factory=list)
    metrics: list[MetricContract] = field(default_factory=list)
    relationships: list[RelationshipContract] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
