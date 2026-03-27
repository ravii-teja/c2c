from __future__ import annotations

import csv
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Iterable

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


class FileSystemConnector(Connector):
    """Scan local folders for common business files and expose lightweight metadata."""

    STRUCTURED_EXTENSIONS = {".csv", ".tsv", ".json"}
    DOCUMENT_EXTENSIONS = {".txt", ".md", ".pdf"}
    BINARY_EXTENSIONS = {".xlsx", ".xls", ".parquet"}
    SUPPORTED_EXTENSIONS = STRUCTURED_EXTENSIONS | DOCUMENT_EXTENSIONS | BINARY_EXTENSIONS

    def __init__(
        self,
        source,
        *,
        include_extensions: set[str] | None = None,
        max_files: int = 500,
    ) -> None:
        super().__init__(source)
        self.include_extensions = {
            extension.lower() if extension.startswith(".") else f".{extension.lower()}"
            for extension in (include_extensions or self.SUPPORTED_EXTENSIONS)
        }
        self.max_files = max_files

    def discover_assets(self) -> list[Asset]:
        base_path = Path(self.source.connection_ref)
        assets: list[Asset] = []

        for index, path in enumerate(self._iter_supported_files(base_path)):
            if index >= self.max_files:
                break
            relative_path = path.relative_to(base_path)
            fields = self._infer_fields(path)
            assets.append(
                Asset(
                    asset_id=f"{self.source.source_id}:{relative_path}",
                    source_id=self.source.source_id,
                    qualified_name=str(relative_path),
                    asset_type=self._asset_type_for_path(path),
                    description=f"Local file discovered by filesystem connector ({path.suffix.lower()})",
                    fields=fields,
                    capabilities=self._capabilities_for_path(path),
                    tags=[path.suffix.lower().lstrip(".")],
                    sensitivity=self._asset_sensitivity(fields, path),
                    policy_tags=self._policy_tags(fields),
                    last_seen_at=datetime.fromtimestamp(path.stat().st_mtime, UTC),
                )
            )

        return assets

    def profile_asset(self, asset: Asset) -> AssetProfile:
        path = Path(self.source.connection_ref) / asset.qualified_name
        row_count = self._row_count(path)
        return AssetProfile(
            asset_id=asset.asset_id,
            row_count_estimate=row_count,
            freshness_hint=datetime.fromtimestamp(path.stat().st_mtime, UTC).isoformat(),
            stats=[
                ProfileStat(name="extension", value=path.suffix.lower()),
                ProfileStat(name="size_bytes", value=path.stat().st_size),
                ProfileStat(name="field_count", value=len(asset.fields)),
            ],
        )

    def sample_asset(self, asset: Asset, limit: int = 5) -> list[SampleRecord]:
        path = Path(self.source.connection_ref) / asset.qualified_name
        extension = path.suffix.lower()
        if extension in {".csv", ".tsv"}:
            return self._sample_delimited(path, limit=limit)
        if extension == ".json":
            return self._sample_json(path, limit=limit)
        if extension in {".txt", ".md"}:
            return [SampleRecord(asset_id=asset.asset_id, values={"preview": self._text_preview(path)})]
        if extension == ".pdf":
            return [
                SampleRecord(
                    asset_id=asset.asset_id,
                    values={
                        "preview": "PDF discovered. Text preview requires a dedicated PDF parser.",
                        "file_name": path.name,
                    },
                )
            ]
        return [
            SampleRecord(
                asset_id=asset.asset_id,
                values={
                    "preview": f"{path.suffix.lower()} discovered. Structured extraction is not yet implemented.",
                    "file_name": path.name,
                },
            )
        ]

    def detect_changes(self) -> list[ChangeEvent]:
        return []

    def list_capabilities(self) -> set[str]:
        return {
            "discover_assets",
            "profile_asset",
            "sample_asset",
            "filesystem_scan",
        }

    def _iter_supported_files(self, base_path: Path) -> Iterable[Path]:
        for path in sorted(base_path.rglob("*")):
            if path.is_file() and path.suffix.lower() in self.include_extensions:
                yield path

    def _infer_fields(self, path: Path) -> list[Field]:
        extension = path.suffix.lower()
        if extension in {".csv", ".tsv"}:
            return self._delimited_fields(path)
        if extension == ".json":
            return self._json_fields(path)
        if extension in {".txt", ".md", ".pdf", ".xlsx", ".xls", ".parquet"}:
            return [
                Field(
                    name="content",
                    field_type=FieldType.STRING,
                    sensitivity=self._field_sensitivity(path.name),
                    policy_tags=self._field_policy_tags(path.name),
                )
            ]
        return []

    def _delimited_fields(self, path: Path) -> list[Field]:
        delimiter = "\t" if path.suffix.lower() == ".tsv" else ","
        with path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.reader(handle, delimiter=delimiter)
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

    def _json_fields(self, path: Path) -> list[Field]:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            return [Field(name="payload", field_type=FieldType.JSON)]

        if isinstance(payload, list) and payload and isinstance(payload[0], dict):
            return [
                Field(
                    name=str(key),
                    field_type=FieldType.STRING,
                    sensitivity=self._field_sensitivity(str(key)),
                    policy_tags=self._field_policy_tags(str(key)),
                )
                for key in payload[0].keys()
            ]
        if isinstance(payload, dict):
            return [
                Field(
                    name=str(key),
                    field_type=FieldType.STRING,
                    sensitivity=self._field_sensitivity(str(key)),
                    policy_tags=self._field_policy_tags(str(key)),
                )
                for key in payload.keys()
            ]
        return [Field(name="payload", field_type=FieldType.JSON)]

    def _asset_type_for_path(self, path: Path) -> AssetType:
        if path.suffix.lower() in self.DOCUMENT_EXTENSIONS:
            return AssetType.DOCUMENT
        return AssetType.FILE

    def _capabilities_for_path(self, path: Path) -> set[AssetCapability]:
        capabilities = {
            AssetCapability.CONTENT_RETRIEVAL,
            AssetCapability.INCREMENTAL_DISCOVERY,
            AssetCapability.FRESHNESS_METADATA,
        }
        if path.suffix.lower() in self.STRUCTURED_EXTENSIONS:
            capabilities.add(AssetCapability.STRUCTURED_QUERY)
        return capabilities

    def _row_count(self, path: Path) -> int | None:
        extension = path.suffix.lower()
        try:
            if extension in {".csv", ".tsv"}:
                delimiter = "\t" if extension == ".tsv" else ","
                with path.open("r", encoding="utf-8", newline="") as handle:
                    reader = csv.DictReader(handle, delimiter=delimiter)
                    return sum(1 for _ in reader)
            if extension == ".json":
                payload = json.loads(path.read_text(encoding="utf-8"))
                if isinstance(payload, list):
                    return len(payload)
                if isinstance(payload, dict):
                    return len(payload)
        except (UnicodeDecodeError, json.JSONDecodeError):
            return None
        return None

    def _sample_delimited(self, path: Path, *, limit: int) -> list[SampleRecord]:
        delimiter = "\t" if path.suffix.lower() == ".tsv" else ","
        base_path = Path(self.source.connection_ref)
        asset_id = f"{self.source.source_id}:{path.relative_to(base_path)}"
        with path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle, delimiter=delimiter)
            return [
                SampleRecord(asset_id=asset_id, values=dict(row))
                for _, row in zip(range(limit), reader)
            ]

    def _sample_json(self, path: Path, *, limit: int) -> list[SampleRecord]:
        base_path = Path(self.source.connection_ref)
        asset_id = f"{self.source.source_id}:{path.relative_to(base_path)}"
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            return [SampleRecord(asset_id=asset_id, values={"preview": "Unreadable JSON payload"})]

        if isinstance(payload, list):
            rows = payload[:limit]
            return [
                SampleRecord(asset_id=asset_id, values=row if isinstance(row, dict) else {"value": row})
                for row in rows
            ]
        if isinstance(payload, dict):
            return [SampleRecord(asset_id=asset_id, values={str(key): value for key, value in payload.items()})]
        return [SampleRecord(asset_id=asset_id, values={"value": payload})]

    def _text_preview(self, path: Path, *, length: int = 500) -> str:
        try:
            return path.read_text(encoding="utf-8")[:length].strip()
        except UnicodeDecodeError:
            return "File is not UTF-8 decodable."

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

    def _asset_sensitivity(self, fields: list[Field], path: Path) -> SensitivityClass:
        if any(field.sensitivity == SensitivityClass.RESTRICTED for field in fields):
            return SensitivityClass.RESTRICTED
        if any(field.sensitivity == SensitivityClass.CONFIDENTIAL for field in fields):
            return SensitivityClass.CONFIDENTIAL
        if path.suffix.lower() == ".pdf":
            return SensitivityClass.INTERNAL
        return SensitivityClass.INTERNAL

    def _policy_tags(self, fields: list[Field]) -> list[str]:
        return sorted({tag for field in fields for tag in field.policy_tags})
