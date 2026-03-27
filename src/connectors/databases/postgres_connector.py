from __future__ import annotations

from .base import DatabaseConnector
from models import Asset, AssetProfile, AssetType, ChangeEvent, Field, SampleRecord


class PostgresConnector(DatabaseConnector):
    """PostgreSQL connector with catalog discovery, profiling, and sampling."""

    platform_name = "PostgreSQL"

    def discover_assets(self) -> list[Asset]:
        asset_rows = self.executor.fetch_all(
            """
            SELECT
              c.table_schema,
              c.table_name,
              t.table_type,
              c.column_name,
              c.data_type,
              c.is_nullable
            FROM information_schema.columns AS c
            JOIN information_schema.tables AS t
              ON c.table_schema = t.table_schema
             AND c.table_name = t.table_name
            WHERE c.table_schema NOT IN ('pg_catalog', 'information_schema')
            ORDER BY c.table_schema, c.table_name, c.ordinal_position
            """
        )

        assets_by_name: dict[str, Asset] = {}
        for row in asset_rows:
            qualified_name = f"{row['table_schema']}.{row['table_name']}"
            if qualified_name not in assets_by_name:
                asset_type = AssetType.VIEW if row["table_type"] == "VIEW" else AssetType.TABLE
                assets_by_name[qualified_name] = self._build_asset(
                    qualified_name=qualified_name,
                    asset_type=asset_type,
                    fields=[],
                    description=f"Discovered from {self.platform_name} information_schema",
                    tags=[row["table_schema"]],
                )

            assets_by_name[qualified_name].fields.append(
                Field(
                    name=row["column_name"],
                    field_type=self._map_field_type(row.get("data_type")),
                    nullable=row.get("is_nullable", "YES") == "YES",
                )
            )

        return list(assets_by_name.values())

    def profile_asset(self, asset: Asset) -> AssetProfile:
        schema_name, table_name = asset.qualified_name.split(".", maxsplit=1)
        freshness_fields = self._candidate_freshness_fields(asset.fields)
        freshness_sql = (
            f'MAX("{freshness_fields[0]}")::text AS freshness_hint'
            if freshness_fields
            else "NULL::text AS freshness_hint"
        )
        profile_row = self.executor.fetch_all(
            f"""
            SELECT
              COUNT(*) AS row_count,
              {freshness_sql}
            FROM "{schema_name}"."{table_name}"
            """.strip()
        )[0]
        return self._profile_from_row(
            asset_id=asset.asset_id,
            row_count=profile_row.get("row_count"),
            freshness_hint=profile_row.get("freshness_hint"),
            extra_stats={"freshness_field": freshness_fields[0] if freshness_fields else None},
        )

    def sample_asset(self, asset: Asset, limit: int = 5) -> list[SampleRecord]:
        schema_name, table_name = asset.qualified_name.split(".", maxsplit=1)
        rows = self.executor.fetch_all(
            f'SELECT * FROM "{schema_name}"."{table_name}" LIMIT {int(limit)}'
        )
        return self._sample_records_from_rows(asset.asset_id, rows)

    def detect_changes(self) -> list[ChangeEvent]:
        return []
