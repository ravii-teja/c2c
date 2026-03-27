from __future__ import annotations

from connectors.databases import BigQueryConnector
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


def test_bigquery_connector_discovers_profiles_and_samples_assets() -> None:
    executor = FakeExecutor(
        {
            "region-us.INFORMATION_SCHEMA.SCHEMATA": [
                {"schema_name": "analytics"}
            ],
            "`analytics`.INFORMATION_SCHEMA.COLUMNS": [
                {
                    "table_schema": "analytics",
                    "table_name": "sessions",
                    "table_type": "BASE TABLE",
                    "column_name": "session_id",
                    "data_type": "INT64",
                    "is_nullable": "NO",
                },
                {
                    "table_schema": "analytics",
                    "table_name": "sessions",
                    "table_type": "BASE TABLE",
                    "column_name": "revenue_amount",
                    "data_type": "FLOAT64",
                    "is_nullable": "YES",
                },
            ],
            "CAST(NULL AS STRING) AS freshness_hint FROM `analytics.sessions`": [
                {"row_count": 128, "freshness_hint": "2026-03-23T12:00:00Z"}
            ],
            "SELECT * FROM `analytics.sessions` LIMIT 3": [
                {"session_id": 10, "revenue_amount": 10.5},
                {"session_id": 11, "revenue_amount": 11.0},
                {"session_id": 12, "revenue_amount": 12.0},
            ],
        }
    )

    connector = BigQueryConnector(
        SourceDefinition(
            source_id="bq1",
            name="Primary BigQuery",
            source_type=SourceType.DATABASE,
            connection_ref="bigquery://project",
        ),
        executor=executor,
    )

    assets = connector.discover_assets()
    assert len(assets) == 1
    assert assets[0].qualified_name == "analytics.sessions"
    assert len(assets[0].fields) == 2

    profile = connector.profile_asset(assets[0])
    assert profile.row_count_estimate == 128
    freshness_field_stat = {stat.name: stat.value for stat in profile.stats}
    assert freshness_field_stat["freshness_field"] is None

    samples = connector.sample_asset(assets[0], limit=3)
    assert len(samples) == 3
    assert samples[2].values["session_id"] == 12
