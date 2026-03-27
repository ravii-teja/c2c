from __future__ import annotations

from connectors.databases import compare_snapshots, snapshot_from_assets
from models import Asset, AssetType, Field, FieldType


def test_compare_snapshots_detects_added_removed_and_changed_assets() -> None:
    previous = snapshot_from_assets(
        "src-1",
        [
            Asset(
                asset_id="src-1:public.orders",
                source_id="src-1",
                qualified_name="public.orders",
                asset_type=AssetType.TABLE,
                fields=[Field(name="id", field_type=FieldType.INTEGER)],
            ),
            Asset(
                asset_id="src-1:public.customers",
                source_id="src-1",
                qualified_name="public.customers",
                asset_type=AssetType.TABLE,
                fields=[Field(name="id", field_type=FieldType.INTEGER)],
            ),
        ],
    )
    current = snapshot_from_assets(
        "src-1",
        [
            Asset(
                asset_id="src-1:public.orders",
                source_id="src-1",
                qualified_name="public.orders",
                asset_type=AssetType.TABLE,
                fields=[
                    Field(name="id", field_type=FieldType.INTEGER),
                    Field(name="total_amount", field_type=FieldType.FLOAT),
                ],
            ),
            Asset(
                asset_id="src-1:public.invoices",
                source_id="src-1",
                qualified_name="public.invoices",
                asset_type=AssetType.TABLE,
                fields=[Field(name="id", field_type=FieldType.INTEGER)],
            ),
        ],
    )

    events = compare_snapshots(previous, current)
    change_types = {event.asset_id: event.change_type for event in events}

    assert change_types["src-1:public.orders"] == "asset_changed"
    assert change_types["src-1:public.customers"] == "asset_removed"
    assert change_types["src-1:public.invoices"] == "asset_added"
