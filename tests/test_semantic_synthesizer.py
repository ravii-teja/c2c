from models import (
    Asset,
    AssetCapability,
    AssetType,
    Field,
    FieldType,
    MetadataGraph,
    RelationshipKind,
    SourceDefinition,
    SourceType,
)
from semantic_layer import SemanticSynthesizer


def test_semantic_synthesizer_generates_entities_and_metric_candidates() -> None:
    graph = MetadataGraph()
    graph.add_source(
        SourceDefinition(
            source_id="src-1",
            name="Example Source",
            source_type=SourceType.FILE_SYSTEM,
            connection_ref="/tmp/example",
        )
    )
    graph.add_asset(
        Asset(
            asset_id="src-1:sales.csv",
            source_id="src-1",
            qualified_name="sales.csv",
            asset_type=AssetType.FILE,
            fields=[
                Field(name="customer_id", field_type=FieldType.STRING),
                Field(name="total_amount", field_type=FieldType.FLOAT),
            ],
            capabilities={AssetCapability.CONTENT_RETRIEVAL},
        )
    )

    draft = SemanticSynthesizer().synthesize(graph)

    assert len(draft.entities) == 1
    assert len(draft.metrics) == 1
    assert draft.metrics[0].name == "total_amount"


def test_semantic_synthesizer_generates_relationship_candidates() -> None:
    graph = MetadataGraph()
    graph.add_source(
        SourceDefinition(
            source_id="src-1",
            name="Example Source",
            source_type=SourceType.FILE_SYSTEM,
            connection_ref="/tmp/example",
        )
    )
    graph.add_asset(
        Asset(
            asset_id="src-1:orders.csv",
            source_id="src-1",
            qualified_name="orders.csv",
            asset_type=AssetType.FILE,
            fields=[
                Field(name="id", field_type=FieldType.INTEGER),
                Field(name="customer_id", field_type=FieldType.INTEGER),
            ],
            capabilities={AssetCapability.CONTENT_RETRIEVAL},
        )
    )
    graph.add_asset(
        Asset(
            asset_id="src-1:customers.csv",
            source_id="src-1",
            qualified_name="customers.csv",
            asset_type=AssetType.FILE,
            fields=[
                Field(name="id", field_type=FieldType.INTEGER),
                Field(name="name", field_type=FieldType.STRING),
            ],
            capabilities={AssetCapability.CONTENT_RETRIEVAL},
        )
    )

    draft = SemanticSynthesizer().synthesize(graph)

    assert len(draft.relationships) == 1
    assert draft.relationships[0].relationship_kind == RelationshipKind.PRIMARY_FOREIGN_KEY
