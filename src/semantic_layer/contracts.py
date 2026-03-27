from __future__ import annotations

import json
from pathlib import Path

from models import (
    ContractStatus,
    EntityContract,
    MetricContract,
    RelationshipContract,
    SensitivityClass,
    SemanticContractBundle,
    SemanticLayerDraft,
)
from org_context import OrganizationContextBundle
from serialization import to_jsonable


class SemanticContractGenerator:
    """Generate reviewable semantic contracts from synthesized semantic drafts."""

    def generate(
        self,
        draft: SemanticLayerDraft,
        owner: str | None = None,
        organization_context: OrganizationContextBundle | None = None,
    ) -> SemanticContractBundle:
        # Contracts are the review surface for the semantic layer, so this step
        # enriches synthesized objects with ownership and governance context.
        entities = [
            EntityContract(
                entity_id=entity.entity_id,
                name=entity.name,
                description=entity.description,
                owner=self._owner_for_name(entity.name, owner, organization_context),
                synonyms=entity.synonyms,
                source_assets=entity.asset_references,
                confidence=entity.confidence,
                status=ContractStatus.DRAFT,
                sensitivity=self._reference_sensitivity(entity.asset_references),
                policy_tags=self._reference_policy_tags(
                    entity.asset_references,
                    entity.name,
                    organization_context,
                ),
            )
            for entity in draft.entities
        ]
        metrics = [
            MetricContract(
                metric_id=metric.metric_id,
                name=metric.name,
                description=metric.description,
                formula_hint=metric.formula_hint,
                grain=metric.grain,
                owner=self._owner_for_name(metric.name, owner, organization_context),
                source_assets=metric.source_assets,
                synonyms=self._metric_synonyms(metric.name, organization_context),
                confidence=metric.confidence,
                status=ContractStatus.DRAFT,
                sensitivity=self._reference_sensitivity(metric.source_assets),
                policy_tags=self._reference_policy_tags(
                    metric.source_assets,
                    metric.name,
                    organization_context,
                ),
                validation_notes=self._validation_notes(metric.formula_hint, metric.confidence),
            )
            for metric in draft.metrics
        ]
        relationships = [
            RelationshipContract(
                relationship_id=(
                    f"relationship:{relationship.left_asset.asset_id}:"
                    f"{relationship.right_asset.asset_id}:"
                    f"{relationship.relationship_kind}"
                ),
                left_asset=relationship.left_asset,
                right_asset=relationship.right_asset,
                relationship_kind=relationship.relationship_kind,
                confidence=relationship.confidence,
                status=ContractStatus.DRAFT,
                sensitivity=self._reference_sensitivity(
                    [relationship.left_asset, relationship.right_asset]
                ),
                policy_tags=self._reference_policy_tags(
                    [relationship.left_asset, relationship.right_asset],
                    relationship.left_asset.qualified_name,
                    organization_context,
                ),
                evidence=relationship.evidence,
                validation_notes=self._relationship_validation_notes(relationship.confidence),
            )
            for relationship in draft.relationships
        ]
        notes = list(draft.notes)
        notes.append("Semantic contract bundle generated from semantic draft.")
        return SemanticContractBundle(
            version=draft.version,
            entities=entities,
            metrics=metrics,
            relationships=relationships,
            notes=notes,
        )

    def _validation_notes(self, formula_hint: str, confidence: float) -> list[str]:
        notes: list[str] = []
        if formula_hint:
            notes.append("Formula hint captured from semantic synthesis output.")
        if confidence < 0.5:
            notes.append("Confidence below 0.5; recommend analyst review before promotion.")
        return notes

    def _relationship_validation_notes(self, confidence: float) -> list[str]:
        notes: list[str] = ["Relationship inferred from metadata heuristics or semantic synthesis."]
        if confidence < 0.5:
            notes.append("Relationship confidence below 0.5; verify join behavior before production use.")
        return notes

    def _reference_sensitivity(self, references) -> SensitivityClass:
        qualified_names = [reference.qualified_name.lower() for reference in references]
        if any(any(token in name for token in ("ssn", "tax", "password")) for name in qualified_names):
            return SensitivityClass.RESTRICTED
        if any(any(token in name for token in ("customer", "employee", "email", "phone")) for name in qualified_names):
            return SensitivityClass.CONFIDENTIAL
        return SensitivityClass.INTERNAL

    def _reference_policy_tags(
        self,
        references,
        semantic_name: str,
        organization_context: OrganizationContextBundle | None,
    ) -> list[str]:
        # Start with repo-native heuristics, then let organization-specific rules
        # override or extend the tags without changing connector code.
        tags: set[str] = set()
        for reference in references:
            lowered = reference.qualified_name.lower()
            if "customer" in lowered:
                tags.add("policy:customer-data")
            if "employee" in lowered:
                tags.add("policy:employee-data")
            if lowered.endswith("_id") or ".id" in lowered:
                tags.add("governance:identifier")
        if organization_context is not None:
            lowered_name = semantic_name.lower()
            for rule in organization_context.governance_rules:
                if any(target.lower() in lowered_name for target in rule.applies_to):
                    tags.update(rule.policy_tags)
        return sorted(tags)

    def _owner_for_name(
        self,
        semantic_name: str,
        fallback_owner: str | None,
        organization_context: OrganizationContextBundle | None,
    ) -> str | None:
        # Glossary ownership wins over defaults because it usually reflects the
        # business steward for a specific term rather than a platform fallback.
        if organization_context is not None and semantic_name in organization_context.glossary:
            glossary_owner = organization_context.glossary[semantic_name].owner
            if glossary_owner:
                return glossary_owner
        if organization_context is not None and organization_context.org_profile.default_metric_owner:
            return organization_context.org_profile.default_metric_owner
        return fallback_owner

    def _metric_synonyms(
        self, metric_name: str, organization_context: OrganizationContextBundle | None
    ) -> list[str]:
        synonyms = [metric_name.replace("_", " ")]
        if organization_context is not None and metric_name in organization_context.glossary:
            synonyms.extend(organization_context.glossary[metric_name].synonyms)
        return sorted(set(synonyms))


class SemanticContractRepository:
    """Persist semantic contract bundles as JSON artifacts."""

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def save(self, bundle: SemanticContractBundle) -> Path:
        path = self.root / f"{bundle.version}-contracts.json"
        path.write_text(json.dumps(to_jsonable(bundle), indent=2, sort_keys=True), encoding="utf-8")
        return path
