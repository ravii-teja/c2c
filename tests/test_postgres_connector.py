from __future__ import annotations

from connectors.databases import PostgresConnector
from models import SourceDefinition, SourceType


class FakeExecutor:
    def __init__(self, responses: dict[str, list[dict]]) -> None:
        self.responses = responses
        self.queries: list[str] = []

    def fetch_all(self, query: str, params=None) -> list[dict]:
        normalized = " ".join(query.split())
        self.queries.append(normalized)
        for needle in sorted(self.responses, key=len, reverse=True):
            response = self.responses[needle]
            if needle in normalized:
                return response
        raise AssertionError(f"Unexpected query: {normalized}")


def test_postgres_connector_discovers_profiles_and_samples_assets() -> None:
    executor = FakeExecutor(
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
                {"row_count": 42, "freshness_hint": "2026-03-23T10:00:00+00:00"}
            ],
            'SELECT * FROM "public"."orders" LIMIT 2': [
                {"order_id": 1, "total_amount": 99.5},
                {"order_id": 2, "total_amount": 101.0},
            ],
        }
    )

    connector = PostgresConnector(
        SourceDefinition(
            source_id="pg1",
            name="Primary Postgres",
            source_type=SourceType.DATABASE,
            connection_ref="postgresql://example",
        ),
        executor=executor,
    )

    assets = connector.discover_assets()
    assert len(assets) == 1
    assert assets[0].qualified_name == "public.orders"
    assert len(assets[0].fields) == 2

    profile = connector.profile_asset(assets[0])
    assert profile.row_count_estimate == 42
    assert profile.freshness_hint == "2026-03-23T10:00:00+00:00"

    freshness_field_stat = {stat.name: stat.value for stat in profile.stats}
    assert freshness_field_stat["freshness_field"] is None

    samples = connector.sample_asset(assets[0], limit=2)
    assert len(samples) == 2
    assert samples[0].values["order_id"] == 1
