from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from models import SourceDefinition, SourceType


@dataclass(slots=True)
class ExecutorConfig:
    kind: str
    module: str | None = None
    factory: str | None = None
    args: list[Any] = field(default_factory=list)
    kwargs: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class SourceRunConfig:
    source_id: str
    source_name: str
    source_type: SourceType
    connection_ref: str
    semantic_version: str = "draft-v1"
    artifact_root: str = ".artifacts"
    context_root: str | None = None
    description: str = ""
    owner: str | None = None
    tags: list[str] = field(default_factory=list)
    executor: ExecutorConfig | None = None

    def to_source_definition(self) -> SourceDefinition:
        return SourceDefinition(
            source_id=self.source_id,
            name=self.source_name,
            source_type=self.source_type,
            connection_ref=self.connection_ref,
            description=self.description,
            owner=self.owner,
            tags=self.tags,
        )


def load_source_run_config(path: str | Path) -> SourceRunConfig:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    executor_payload = payload.get("executor")
    executor = None
    if executor_payload is not None:
        executor = ExecutorConfig(
            kind=executor_payload["kind"],
            module=executor_payload.get("module"),
            factory=executor_payload.get("factory"),
            args=executor_payload.get("args", []),
            kwargs=executor_payload.get("kwargs", {}),
        )

    return SourceRunConfig(
        source_id=payload["source_id"],
        source_name=payload["source_name"],
        source_type=SourceType(payload["source_type"]),
        connection_ref=payload["connection_ref"],
        semantic_version=payload.get("semantic_version", "draft-v1"),
        artifact_root=payload.get("artifact_root", ".artifacts"),
        context_root=payload.get("context_root"),
        description=payload.get("description", ""),
        owner=payload.get("owner"),
        tags=payload.get("tags", []),
        executor=executor,
    )
