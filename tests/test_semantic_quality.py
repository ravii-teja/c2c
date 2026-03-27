from evaluation import SemanticBenchmarkDefinition, SemanticQualityScorer
from models import (
    AssetReference,
    ContractStatus,
    EntityContract,
    MetricContract,
    RelationshipContract,
    RelationshipKind,
    SemanticContractBundle,
)


def test_semantic_quality_scorer_scores_contracts_against_benchmark() -> None:
    benchmark = SemanticBenchmarkDefinition(
        benchmark_id="sales-v1",
        entity_names=["orders", "customers"],
        metric_names=["total_amount"],
        relationships=["orders|customers|primary_foreign_key"],
        required_policy_tags=["policy:customer-data", "governance:identifier"],
    )
    contracts = SemanticContractBundle(
        version="draft-v1",
        entities=[
            EntityContract(
                entity_id="entity:orders",
                name="orders",
                source_assets=[
                    AssetReference(asset_id="src:orders", qualified_name="orders", source_id="src")
                ],
                status=ContractStatus.DRAFT,
                policy_tags=["governance:identifier"],
            )
        ],
        metrics=[
            MetricContract(
                metric_id="metric:total_amount",
                name="total_amount",
                source_assets=[
                    AssetReference(asset_id="src:orders", qualified_name="orders", source_id="src")
                ],
                status=ContractStatus.DRAFT,
                policy_tags=["governance:identifier"],
            )
        ],
        relationships=[
            RelationshipContract(
                relationship_id="relationship:orders:customers",
                left_asset=AssetReference(
                    asset_id="src:orders",
                    qualified_name="orders",
                    source_id="src",
                ),
                right_asset=AssetReference(
                    asset_id="src:customers",
                    qualified_name="customers",
                    source_id="src",
                ),
                relationship_kind=RelationshipKind.PRIMARY_FOREIGN_KEY,
                status=ContractStatus.DRAFT,
                policy_tags=["policy:customer-data", "governance:identifier"],
            )
        ],
    )

    report = SemanticQualityScorer().score(benchmark, contracts)

    assert report.entity_precision == 1.0
    assert report.entity_recall == 0.5
    assert report.metric_precision == 1.0
    assert report.metric_recall == 1.0
    assert report.relationship_precision == 1.0
    assert report.relationship_recall == 1.0
    assert report.governance_tag_recall == 1.0
