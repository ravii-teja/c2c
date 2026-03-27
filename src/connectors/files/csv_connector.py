from __future__ import annotations

import csv
from datetime import datetime, UTC
from pathlib import Path

from connectors.base import Connector
from models import (
    Asset,
    AssetCapability,
    AssetProfile,
    AssetType,
    ChangeEvent,
    Field,
    FieldType,
    ProfileStat,
    SampleRecord,
    SensitivityClass,
)


class CsvConnector(Connector):
    """Simple file-based connector for local CSV discovery."""

    def discover_assets(self) -> list[Asset]:
        base_path = Path(self.source.connection_ref)
        assets: list[Asset] = []

        for path in sorted(base_path.rglob("*.csv")):
            fields = self._infer_fields(path)
            asset_id = f"{self.source.source_id}:{path.relative_to(base_path)}"
            assets.append(
                Asset(
                    asset_id=asset_id,
                    source_id=self.source.source_id,
                    qualified_name=str(path.relative_to(base_path)),
                    asset_type=AssetType.FILE,
                    description="CSV file discovered from file connector",
                    fields=fields,
                    capabilities={
                        AssetCapability.CONTENT_RETRIEVAL,
                        AssetCapability.INCREMENTAL_DISCOVERY,
                        AssetCapability.FRESHNESS_METADATA,
                    },
                    sensitivity=self._asset_sensitivity(fields),
                    policy_tags=self._policy_tags(fields),
                    last_seen_at=datetime.now(UTC),
                )
            )

        return assets

    def profile_asset(self, asset: Asset) -> AssetProfile:
        path = Path(self.source.connection_ref) / asset.qualified_name
        row_count = 0
        with path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            for _ in reader:
                row_count += 1

        return AssetProfile(
            asset_id=asset.asset_id,
            row_count_estimate=row_count,
            freshness_hint=datetime.fromtimestamp(path.stat().st_mtime, UTC).isoformat(),
            stats=[ProfileStat(name="field_count", value=len(asset.fields))],
        )

    def sample_asset(self, asset: Asset, limit: int = 5) -> list[SampleRecord]:
        path = Path(self.source.connection_ref) / asset.qualified_name
        samples: list[SampleRecord] = []

        with path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            for index, row in enumerate(reader):
                if index >= limit:
                    break
                samples.append(SampleRecord(asset_id=asset.asset_id, values=dict(row)))

        return samples

    def detect_changes(self) -> list[ChangeEvent]:
        return []

    def list_capabilities(self) -> set[str]:
        return {
            "discover_assets",
            "profile_asset",
            "sample_asset",
            "incremental_file_scan",
        }

    def _infer_fields(self, path: Path) -> list[Field]:
        with path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.reader(handle)
            headers = next(reader, [])
        return [
            Field(
                name=header,
                field_type=FieldType.STRING,
                sensitivity=self._field_sensitivity(header),
                policy_tags=self._field_policy_tags(header),
            )
            for header in headers
        ]

    def _field_sensitivity(self, field_name: str) -> SensitivityClass:
        lowered = field_name.lower()
        if any(token in lowered for token in ("ssn", "social_security", "tax_id", "password")):
            return SensitivityClass.RESTRICTED
        if any(token in lowered for token in ("email", "phone", "address", "customer_id", "employee_id")):
            return SensitivityClass.CONFIDENTIAL
        return SensitivityClass.INTERNAL

    def _field_policy_tags(self, field_name: str) -> list[str]:
        lowered = field_name.lower()
        tags: list[str] = []
        if "email" in lowered:
            tags.append("pii:email")
        if "phone" in lowered:
            tags.append("pii:phone")
        if "address" in lowered:
            tags.append("pii:address")
        if any(token in lowered for token in ("ssn", "social_security", "tax_id")):
            tags.append("regulated:high-risk-identifier")
        if lowered.endswith("_id"):
            tags.append("governance:identifier")
        return tags

    def _asset_sensitivity(self, fields: list[Field]) -> SensitivityClass:
        if any(field.sensitivity == SensitivityClass.RESTRICTED for field in fields):
            return SensitivityClass.RESTRICTED
        if any(field.sensitivity == SensitivityClass.CONFIDENTIAL for field in fields):
            return SensitivityClass.CONFIDENTIAL
        return SensitivityClass.INTERNAL

    def _policy_tags(self, fields: list[Field]) -> list[str]:
        tags = {tag for field in fields for tag in field.policy_tags}
        return sorted(tags)
