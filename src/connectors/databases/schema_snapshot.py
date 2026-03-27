from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, UTC
from hashlib import sha256

from models import Asset, ChangeEvent


@dataclass(slots=True)
class SchemaSnapshot:
    source_id: str
    captured_at: datetime
    asset_signatures: dict[str, str] = field(default_factory=dict)


def snapshot_from_assets(source_id: str, assets: list[Asset]) -> SchemaSnapshot:
    return SchemaSnapshot(
        source_id=source_id,
        captured_at=datetime.now(UTC),
        asset_signatures={asset.asset_id: _asset_signature(asset) for asset in assets},
    )


def compare_snapshots(previous: SchemaSnapshot, current: SchemaSnapshot) -> list[ChangeEvent]:
    events: list[ChangeEvent] = []
    previous_ids = set(previous.asset_signatures)
    current_ids = set(current.asset_signatures)

    for asset_id in sorted(current_ids - previous_ids):
        events.append(
            ChangeEvent(
                asset_id=asset_id,
                change_type="asset_added",
                detected_at=current.captured_at,
                summary="Asset added to source snapshot.",
            )
        )
    for asset_id in sorted(previous_ids - current_ids):
        events.append(
            ChangeEvent(
                asset_id=asset_id,
                change_type="asset_removed",
                detected_at=current.captured_at,
                summary="Asset removed from source snapshot.",
            )
        )
    for asset_id in sorted(previous_ids & current_ids):
        if previous.asset_signatures[asset_id] != current.asset_signatures[asset_id]:
            events.append(
                ChangeEvent(
                    asset_id=asset_id,
                    change_type="asset_changed",
                    detected_at=current.captured_at,
                    summary="Asset schema changed between snapshots.",
                )
            )

    return events


def _asset_signature(asset: Asset) -> str:
    payload = "|".join(
        [asset.qualified_name, asset.asset_type]
        + [f"{field.name}:{field.field_type}:{field.nullable}" for field in asset.fields]
    )
    return sha256(payload.encode("utf-8")).hexdigest()
