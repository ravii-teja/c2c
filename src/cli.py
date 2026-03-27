from __future__ import annotations

import argparse
import json

from config import load_source_run_config
from workflows import (
    run_bigquery_workflow,
    run_local_csv_workflow,
    run_local_filesystem_workflow,
    run_postgres_workflow,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="c2c",
        description="Chaos 2 Clarity workflow runner",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    local_csv = subparsers.add_parser(
        "run-local-csv",
        help="Run discovery and semantic synthesis for a local CSV folder.",
    )
    local_csv.add_argument("--csv-root", required=True, help="Path to the CSV folder.")
    local_csv.add_argument(
        "--artifact-root",
        default=".artifacts",
        help="Artifact root where metadata, schema, semantic, and run summaries are stored.",
    )
    local_csv.add_argument("--source-id", default="local-csv", help="Source identifier.")
    local_csv.add_argument("--source-name", default="Local CSV Source", help="Source display name.")
    local_csv.add_argument(
        "--semantic-version",
        default="draft-v1",
        help="Version label for the synthesized semantic draft.",
    )
    local_csv.add_argument(
        "--context-root",
        default=None,
        help="Optional organization-context folder containing glossary, governance rules, and org context.",
    )

    local_filesystem = subparsers.add_parser(
        "run-local-filesystem",
        help="Run discovery and semantic synthesis for a local filesystem scan.",
    )
    local_filesystem.add_argument("--root-path", required=True, help="Folder path to scan.")
    local_filesystem.add_argument(
        "--artifact-root",
        default=".artifacts",
        help="Artifact root where metadata, schema, semantic, and run summaries are stored.",
    )
    local_filesystem.add_argument(
        "--source-id",
        default="local-filesystem",
        help="Source identifier.",
    )
    local_filesystem.add_argument(
        "--source-name",
        default="Local Filesystem Source",
        help="Source display name.",
    )
    local_filesystem.add_argument(
        "--semantic-version",
        default="draft-v1",
        help="Version label for the synthesized semantic draft.",
    )
    local_filesystem.add_argument(
        "--context-root",
        default=None,
        help="Optional organization-context folder containing glossary, governance rules, and org context.",
    )
    local_filesystem.add_argument(
        "--extensions",
        nargs="*",
        default=None,
        help="Optional list of file extensions to include, such as csv pdf md json.",
    )
    local_filesystem.add_argument(
        "--max-files",
        type=int,
        default=500,
        help="Maximum number of files to scan in one run.",
    )

    postgres = subparsers.add_parser(
        "run-postgres",
        help="Run discovery and semantic synthesis for a PostgreSQL source from a JSON config.",
    )
    postgres.add_argument("--config", required=True, help="Path to a JSON source config.")

    bigquery = subparsers.add_parser(
        "run-bigquery",
        help="Run discovery and semantic synthesis for a BigQuery source from a JSON config.",
    )
    bigquery.add_argument("--config", required=True, help="Path to a JSON source config.")
    return parser


def _result_payload(result) -> dict[str, str | int]:
    return {
        "asset_count": result.asset_count,
        "entity_count": result.entity_count,
        "metric_count": result.metric_count,
        "drift_event_count": result.drift_event_count,
        "artifact_root": str(result.artifact_layout.root),
        "metadata_path": str(result.metadata_path),
        "semantic_path": str(result.semantic_path),
        "contract_path": str(result.contract_path),
        "run_summary_path": str(result.run_summary_path),
    }


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "run-local-csv":
        result = run_local_csv_workflow(
            csv_root=args.csv_root,
            artifact_root=args.artifact_root,
            source_id=args.source_id,
            source_name=args.source_name,
            semantic_version=args.semantic_version,
            context_root=args.context_root,
        )
        print(json.dumps(_result_payload(result), indent=2, sort_keys=True))
        return 0

    if args.command == "run-postgres":
        result = run_postgres_workflow(load_source_run_config(args.config))
        print(json.dumps(_result_payload(result), indent=2, sort_keys=True))
        return 0

    if args.command == "run-local-filesystem":
        extensions = None
        if args.extensions:
            extensions = {
                extension if extension.startswith(".") else f".{extension}"
                for extension in args.extensions
            }
        result = run_local_filesystem_workflow(
            root_path=args.root_path,
            artifact_root=args.artifact_root,
            source_id=args.source_id,
            source_name=args.source_name,
            semantic_version=args.semantic_version,
            context_root=args.context_root,
            include_extensions=extensions,
            max_files=args.max_files,
        )
        print(json.dumps(_result_payload(result), indent=2, sort_keys=True))
        return 0

    if args.command == "run-bigquery":
        result = run_bigquery_workflow(load_source_run_config(args.config))
        print(json.dumps(_result_payload(result), indent=2, sort_keys=True))
        return 0

    parser.error(f"Unsupported command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
