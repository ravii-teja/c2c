from __future__ import annotations

from models import (
    AssetReference,
    CandidateRelationship,
    CanonicalEntity,
    CanonicalMetric,
    MetadataGraph,
    RelationshipKind,
    SemanticLayerDraft,
)
from org_context import OrganizationContextBundle


class SemanticSynthesizer:
    """
    Starter semantic synthesizer.

    This first version uses deterministic heuristics so we can establish
    the semantic object model before layering in LLM-assisted enrichment.
    """

    def synthesize(
        self,
        graph: MetadataGraph,
        version: str = "draft-v1",
        organization_context: OrganizationContextBundle | None = None,
    ) -> SemanticLayerDraft:
        entities: list[CanonicalEntity] = []
        metrics: list[CanonicalMetric] = []
        relationships: list[CandidateRelationship] = []
        notes: list[str] = []

        # Keep lightweight lookup maps so we can derive cross-asset relationships
        # after the first pass without re-walking the metadata graph.
        asset_refs: dict[str, AssetReference] = {}
        asset_fields: dict[str, list[str]] = {}
        asset_names: dict[str, str] = {}

        for asset in graph.assets.values():
            asset_ref = AssetReference(
                asset_id=asset.asset_id,
                qualified_name=asset.qualified_name,
                source_id=asset.source_id,
            )
            asset_refs[asset.asset_id] = asset_ref
            asset_fields[asset.asset_id] = [field.name for field in asset.fields]
            entity_name = self._entity_name_from_asset(asset.qualified_name)
            asset_names[asset.asset_id] = entity_name
            entities.append(
                CanonicalEntity(
                    entity_id=f"entity:{asset.asset_id}",
                    name=entity_name,
                    description=f"Candidate entity synthesized from {asset.qualified_name}",
                    synonyms=self._entity_synonyms(
                        entity_name,
                        asset.qualified_name,
                        organization_context,
                    ),
                    asset_references=[asset_ref],
                    confidence=0.45,
                )
            )

            asset_metrics = self._metric_candidates(asset_ref, [field.name for field in asset.fields])
            metrics.extend(asset_metrics)

        relationships.extend(self._relationship_candidates(asset_refs, asset_fields, asset_names))

        if not graph.assets:
            notes.append("No assets discovered; semantic synthesis skipped.")
        else:
            notes.append(
                "Draft semantic layer synthesized from discovered assets using deterministic heuristics."
            )
        if organization_context is not None and organization_context.org_profile.company_name:
            notes.append(
                "Semantic synthesis incorporated organization context for "
                f"{organization_context.org_profile.company_name}."
            )

        return SemanticLayerDraft(
            version=version,
            entities=entities,
            metrics=metrics,
            relationships=relationships,
            notes=notes,
        )

    def _entity_name_from_asset(self, qualified_name: str) -> str:
        stem = qualified_name.rsplit("/", maxsplit=1)[-1]
        stem = stem.rsplit(".", maxsplit=1)[0]
        return stem.replace("-", "_")

    def _metric_candidates(
        self, asset_ref: AssetReference, field_names: list[str]
    ) -> list[CanonicalMetric]:
        metrics: list[CanonicalMetric] = []
        for field_name in field_names:
            lowered = field_name.lower()
            if any(token in lowered for token in ("amount", "revenue", "cost", "price", "total", "count")):
                metrics.append(
                    CanonicalMetric(
                        metric_id=f"metric:{asset_ref.asset_id}:{field_name}",
                        name=field_name,
                        description=f"Candidate metric inferred from field '{field_name}'",
                        formula_hint=f"Aggregate {field_name} with sum or count depending on business grain.",
                        grain="source_asset",
                        source_assets=[asset_ref],
                        confidence=0.40,
                    )
                )
        return metrics

    def _entity_synonyms(
        self,
        entity_name: str,
        qualified_name: str,
        organization_context: OrganizationContextBundle | None,
    ) -> list[str]:
        synonyms = [qualified_name, entity_name.replace("_", " ")]
        if organization_context is not None and entity_name in organization_context.glossary:
            synonyms.extend(organization_context.glossary[entity_name].synonyms)
        return sorted(set(synonyms))

    def _relationship_candidates(
        self,
        asset_refs: dict[str, AssetReference],
        asset_fields: dict[str, list[str]],
        asset_names: dict[str, str],
    ) -> list[CandidateRelationship]:
        relationships: list[CandidateRelationship] = []
        asset_ids = sorted(asset_refs)

        for left_index, left_asset_id in enumerate(asset_ids):
            left_fields = {field.lower() for field in asset_fields[left_asset_id]}
            left_name = asset_names[left_asset_id]
            left_key = self._singularize(left_name)
            for right_asset_id in asset_ids[left_index + 1 :]:
                right_fields = {field.lower() for field in asset_fields[right_asset_id]}
                right_name = asset_names[right_asset_id]
                right_key = self._singularize(right_name)

                # Prefer explicit foreign-key style matches first, then fall back to
                # weaker shared-identifier hints so downstream review can distinguish them.
                if f"{right_key}_id" in left_fields and "id" in right_fields:
                    relationships.append(
                        CandidateRelationship(
                            left_asset=asset_refs[left_asset_id],
                            right_asset=asset_refs[right_asset_id],
                            relationship_kind=RelationshipKind.PRIMARY_FOREIGN_KEY,
                            confidence=0.65,
                            evidence=f"Field '{right_key}_id' in {left_name} matches 'id' in {right_name}.",
                        )
                    )
                elif f"{left_key}_id" in right_fields and "id" in left_fields:
                    relationships.append(
                        CandidateRelationship(
                            left_asset=asset_refs[right_asset_id],
                            right_asset=asset_refs[left_asset_id],
                            relationship_kind=RelationshipKind.PRIMARY_FOREIGN_KEY,
                            confidence=0.65,
                            evidence=f"Field '{left_key}_id' in {right_name} matches 'id' in {left_name}.",
                        )
                    )
                else:
                    shared_id_fields = sorted(
                        field for field in (left_fields & right_fields) if field.endswith("_id")
                    )
                    if shared_id_fields:
                        relationships.append(
                            CandidateRelationship(
                                left_asset=asset_refs[left_asset_id],
                                right_asset=asset_refs[right_asset_id],
                                relationship_kind=RelationshipKind.SOFT_MATCH,
                                confidence=0.35,
                                evidence=(
                                    f"Shared identifier-like fields detected: {', '.join(shared_id_fields)}."
                                ),
                            )
                        )

        return relationships

    def _singularize(self, name: str) -> str:
        return name[:-1] if name.endswith("s") and len(name) > 1 else name
