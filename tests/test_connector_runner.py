from __future__ import annotations

from connectors.databases import PostgresConnector
from discovery import ConnectorRunner, SchemaSnapshotRepository
from models import SourceDefinition, SourceType


class FakeExecutor:
    def __init__(self, responses: dict[str, list[dict]]) -> None:
        self.responses = responses

    def fetch_all(self, query: str, params=None) -> list[dict]:
        normalized = " ".join(query.split())
        for needle in sorted(self.responses, key=len, reverse=True):
            response = self.responses[needle]
            if needle in normalized:
                return response
        raise AssertionError(f"Unexpected query: {normalized}")


def _build_connector(executor: FakeExecutor) -> PostgresConnector:
    return PostgresConnector(
        SourceDefinition(
            source_id="pg1",
            name="Primary Postgres",
            source_type=SourceType.DATABASE,
            connection_ref="postgresql://example",
        ),
        executor=executor,
    )


def test_connector_runner_persists_snapshot_and_emits_drift_events(tmp_path) -> None:
    first_run_executor = FakeExecutor(
        {
            "FROM information_schema.columns": [
                {
                    "table_schema": "public",
                    "table_name": "orders",
                    "table_type": "BASE TABLE",
                    "column_name": "order_id",
                    "data_type": "bigint",
                    "is_nullable": "NO",
                }
            ],
            'SELECT COUNT(*) AS row_count, NULL::text AS freshness_hint FROM "public"."orders"': [
                {"row_count": 10, "freshness_hint": None}
            ],
            'SELECT * FROM "public"."orders" LIMIT 5': [{"order_id": 1}],
        }
    )
    second_run_executor = FakeExecutor(
        {
            "FROM information_schema.columns": [
                {
                    "table_schema": "public",
                    "table_name": "orders",
                    "table_type": "BASE TABLE",
                    "column_name": "order_id",
                    "data_type": "bigint",
                    "is_nullable": "NO",
                },
                {
                    "table_schema": "public",
                    "table_name": "orders",
                    "table_type": "BASE TABLE",
                    "column_name": "total_amount",
                    "data_type": "numeric",
                    "is_nullable": "YES",
                },
            ],
            'SELECT COUNT(*) AS row_count, NULL::text AS freshness_hint FROM "public"."orders"': [
                {"row_count": 11, "freshness_hint": None}
            ],
            'SELECT * FROM "public"."orders" LIMIT 5': [{"order_id": 1, "total_amount": 10.5}],
        }
    )

    repository = SchemaSnapshotRepository(tmp_path)
    runner = ConnectorRunner(repository)

    first_result = runner.run(_build_connector(first_run_executor))
    second_result = runner.run(_build_connector(second_run_executor))

    assert first_result.snapshot_saved is True
    assert first_result.drift_event_count == 0
    assert second_result.snapshot_saved is True
    assert second_result.drift_event_count == 1
    assert second_result.graph.change_events[0].change_type == "asset_changed"
