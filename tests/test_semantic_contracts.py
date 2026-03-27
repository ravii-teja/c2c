from models import (
    AssetReference,
    CandidateRelationship,
    CanonicalEntity,
    CanonicalMetric,
    RelationshipKind,
    SemanticLayerDraft,
)
from semantic_layer import SemanticContractGenerator, SemanticContractRepository


def test_semantic_contract_generator_creates_contract_bundle(tmp_path) -> None:
    draft = SemanticLayerDraft(
        version="draft-v1",
        entities=[
            CanonicalEntity(
                entity_id="entity:orders",
                name="orders",
                asset_references=[
                    AssetReference(asset_id="src:orders", qualified_name="orders", source_id="src")
                ],
                confidence=0.6,
            )
        ],
        metrics=[
            CanonicalMetric(
                metric_id="metric:total_amount",
                name="total_amount",
                formula_hint="sum(total_amount)",
                grain="order",
                source_assets=[
                    AssetReference(asset_id="src:orders", qualified_name="orders", source_id="src")
                ],
                confidence=0.4,
            )
        ],
        relationships=[
            CandidateRelationship(
                left_asset=AssetReference(
                    asset_id="src:orders", qualified_name="orders", source_id="src"
                ),
                right_asset=AssetReference(
                    asset_id="src:customers", qualified_name="customers", source_id="src"
                ),
                relationship_kind=RelationshipKind.PRIMARY_FOREIGN_KEY,
                confidence=0.7,
                evidence="orders.customer_id joins to customers.id",
            )
        ],
    )

    bundle = SemanticContractGenerator().generate(draft, owner="finance")
    saved_path = SemanticContractRepository(tmp_path).save(bundle)

    assert bundle.version == "draft-v1"
    assert bundle.metrics[0].owner == "finance"
    assert "analyst review" in bundle.metrics[0].validation_notes[1]
    assert bundle.relationships[0].relationship_kind == RelationshipKind.PRIMARY_FOREIGN_KEY
    assert saved_path.exists()
