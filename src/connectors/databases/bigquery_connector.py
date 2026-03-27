from __future__ import annotations

from models import Asset, AssetProfile, AssetType, ChangeEvent, Field, SampleRecord

from .base import DatabaseConnector


class BigQueryConnector(DatabaseConnector):
    """BigQuery connector with information schema discovery, profiling, and sampling."""

    platform_name = "BigQuery"

    def discover_assets(self) -> list[Asset]:
        dataset_rows = self.executor.fetch_all(
            "SELECT schema_name FROM region-us.INFORMATION_SCHEMA.SCHEMATA ORDER BY schema_name"
        )

        assets: list[Asset] = []
        for dataset_row in dataset_rows:
            dataset = dataset_row["schema_name"]
            column_rows = self.executor.fetch_all(
                f"""
                SELECT
                  c.table_schema,
                  c.table_name,
                  t.table_type,
                  c.column_name,
                  c.data_type,
                  c.is_nullable
                FROM `{dataset}`.INFORMATION_SCHEMA.COLUMNS AS c
                JOIN `{dataset}`.INFORMATION_SCHEMA.TABLES AS t
                  ON c.table_schema = t.table_schema
                 AND c.table_name = t.table_name
                ORDER BY c.table_name, c.ordinal_position
                """.strip()
            )

            assets_by_name: dict[str, Asset] = {}
            for row in column_rows:
                qualified_name = f"{row['table_schema']}.{row['table_name']}"
                if qualified_name not in assets_by_name:
                    asset_type = AssetType.VIEW if row["table_type"] == "VIEW" else AssetType.TABLE
                    assets_by_name[qualified_name] = self._build_asset(
                        qualified_name=qualified_name,
                        asset_type=asset_type,
                        fields=[],
                        description=f"Discovered from {self.platform_name} INFORMATION_SCHEMA",
                        tags=[row["table_schema"]],
                    )

                assets_by_name[qualified_name].fields.append(
                    Field(
                        name=row["column_name"],
                        field_type=self._map_field_type(row.get("data_type")),
                        nullable=row.get("is_nullable", "YES") == "YES",
                    )
                )

            assets.extend(assets_by_name.values())

        return assets

    def profile_asset(self, asset: Asset) -> AssetProfile:
        freshness_fields = self._candidate_freshness_fields(asset.fields)
        freshness_sql = (
            f"CAST(MAX(`{freshness_fields[0]}`) AS STRING) AS freshness_hint"
            if freshness_fields
            else "CAST(NULL AS STRING) AS freshness_hint"
        )
        row = self.executor.fetch_all(
            f"""
            SELECT
              COUNT(*) AS row_count,
              {freshness_sql}
            FROM `{asset.qualified_name}`
            """.strip()
        )[0]
        return self._profile_from_row(
            asset_id=asset.asset_id,
            row_count=row.get("row_count"),
            freshness_hint=row.get("freshness_hint"),
            extra_stats={"freshness_field": freshness_fields[0] if freshness_fields else None},
        )

    def sample_asset(self, asset: Asset, limit: int = 5) -> list[SampleRecord]:
        rows = self.executor.fetch_all(
            f"SELECT * FROM `{asset.qualified_name}` LIMIT {int(limit)}"
        )
        return self._sample_records_from_rows(asset.asset_id, rows)

    def detect_changes(self) -> list[ChangeEvent]:
        return []
