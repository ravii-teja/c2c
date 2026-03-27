from __future__ import annotations

from cli import build_parser


def test_cli_parser_accepts_local_csv_command() -> None:
    parser = build_parser()

    args = parser.parse_args(
        [
            "run-local-csv",
            "--csv-root",
            "/tmp/data",
            "--artifact-root",
            "/tmp/artifacts",
            "--context-root",
            "/tmp/organization_context",
        ]
    )

    assert args.command == "run-local-csv"
    assert args.csv_root == "/tmp/data"
    assert args.artifact_root == "/tmp/artifacts"
    assert args.context_root == "/tmp/organization_context"


def test_cli_parser_accepts_postgres_command() -> None:
    parser = build_parser()

    args = parser.parse_args(
        [
            "run-postgres",
            "--config",
            "/tmp/postgres.json",
        ]
    )

    assert args.command == "run-postgres"
    assert args.config == "/tmp/postgres.json"


def test_cli_parser_accepts_local_filesystem_command() -> None:
    parser = build_parser()

    args = parser.parse_args(
        [
            "run-local-filesystem",
            "--root-path",
            "/tmp/workspace",
            "--artifact-root",
            "/tmp/artifacts",
            "--extensions",
            "csv",
            "pdf",
        ]
    )

    assert args.command == "run-local-filesystem"
    assert args.root_path == "/tmp/workspace"
    assert args.artifact_root == "/tmp/artifacts"
    assert args.extensions == ["csv", "pdf"]
