from __future__ import annotations

from workflows import run_local_csv_workflow


def run_local_csv_pipeline(csv_root: str) -> None:
    result = run_local_csv_workflow(
        csv_root=csv_root,
        artifact_root=".artifacts",
        source_id="local-csv",
        source_name="Local CSV Source",
    )

    print(f"Discovered {result.asset_count} assets")
    print(f"Synthesized {result.entity_count} entities")
    print(f"Synthesized {result.metric_count} metrics")
    print(f"Metadata saved to {result.metadata_path}")
    print(f"Semantic draft saved to {result.semantic_path}")


if __name__ == "__main__":
    run_local_csv_pipeline("data")
