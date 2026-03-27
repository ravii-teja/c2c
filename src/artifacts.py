from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class ArtifactLayout:
    root: Path
    metadata_dir: Path
    schema_dir: Path
    semantic_dir: Path
    runs_dir: Path


def ensure_artifact_layout(root: str | Path) -> ArtifactLayout:
    root_path = Path(root)
    metadata_dir = root_path / "metadata"
    schema_dir = root_path / "schema"
    semantic_dir = root_path / "semantic"
    runs_dir = root_path / "runs"

    for path in (root_path, metadata_dir, schema_dir, semantic_dir, runs_dir):
        path.mkdir(parents=True, exist_ok=True)

    return ArtifactLayout(
        root=root_path,
        metadata_dir=metadata_dir,
        schema_dir=schema_dir,
        semantic_dir=semantic_dir,
        runs_dir=runs_dir,
    )
