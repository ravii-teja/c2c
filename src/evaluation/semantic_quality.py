from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from models import SemanticContractBundle


@dataclass(slots=True)
class SemanticBenchmarkDefinition:
    benchmark_id: str
    entity_names: list[str] = field(default_factory=list)
    metric_names: list[str] = field(default_factory=list)
    relationships: list[str] = field(default_factory=list)
    required_policy_tags: list[str] = field(default_factory=list)


@dataclass(slots=True)
class SemanticQualityReport:
    benchmark_id: str
    entity_precision: float
    entity_recall: float
    metric_precision: float
    metric_recall: float
    relationship_precision: float
    relationship_recall: float
    governance_tag_recall: float


class SemanticBenchmarkLoader:
    def load(self, path: str | Path) -> SemanticBenchmarkDefinition:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        return SemanticBenchmarkDefinition(
            benchmark_id=payload["benchmark_id"],
            entity_names=payload.get("entity_names", []),
            metric_names=payload.get("metric_names", []),
            relationships=payload.get("relationships", []),
            required_policy_tags=payload.get("required_policy_tags", []),
        )


class SemanticQualityScorer:
    def score(
        self,
        benchmark: SemanticBenchmarkDefinition,
        contracts: SemanticContractBundle,
    ) -> SemanticQualityReport:
        predicted_entities = {entity.name for entity in contracts.entities}
        predicted_metrics = {metric.name for metric in contracts.metrics}
        predicted_relationships = {
            _relationship_signature(
                relationship.left_asset.qualified_name,
                relationship.right_asset.qualified_name,
                relationship.relationship_kind,
            )
            for relationship in contracts.relationships
        }
        gold_entities = set(benchmark.entity_names)
        gold_metrics = set(benchmark.metric_names)
        gold_relationships = set(benchmark.relationships)
        observed_policy_tags = {
            tag
            for contract in [*contracts.entities, *contracts.metrics, *contracts.relationships]
            for tag in contract.policy_tags
        }
        required_policy_tags = set(benchmark.required_policy_tags)

        return SemanticQualityReport(
            benchmark_id=benchmark.benchmark_id,
            entity_precision=_precision(predicted_entities, gold_entities),
            entity_recall=_recall(predicted_entities, gold_entities),
            metric_precision=_precision(predicted_metrics, gold_metrics),
            metric_recall=_recall(predicted_metrics, gold_metrics),
            relationship_precision=_precision(predicted_relationships, gold_relationships),
            relationship_recall=_recall(predicted_relationships, gold_relationships),
            governance_tag_recall=_recall(observed_policy_tags, required_policy_tags),
        )


def _precision(predicted: set[str], gold: set[str]) -> float:
    if not predicted:
        return 0.0
    return round(len(predicted & gold) / len(predicted), 4)


def _recall(predicted: set[str], gold: set[str]) -> float:
    if not gold:
        return 0.0
    return round(len(predicted & gold) / len(gold), 4)


def _relationship_signature(left_qualified_name: str, right_qualified_name: str, relationship_kind) -> str:
    return f"{left_qualified_name}|{right_qualified_name}|{relationship_kind}"
