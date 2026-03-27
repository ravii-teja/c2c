from __future__ import annotations

from config import load_source_run_config


def test_load_source_run_config_parses_executor(tmp_path) -> None:
    tmp_path.mkdir(parents=True, exist_ok=True)
    config_path = tmp_path / "postgres.json"
    config_path.write_text(
        """
        {
          "source_id": "pg-prod",
          "source_name": "Production Postgres",
          "source_type": "database",
          "connection_ref": "postgresql://warehouse",
          "artifact_root": ".artifacts",
          "context_root": "./organization_context",
          "semantic_version": "draft-v2",
          "executor": {
            "kind": "dbapi",
            "module": "tests.fake_dbapi_module",
            "kwargs": {"dsn": "postgresql://warehouse"}
          }
        }
        """,
        encoding="utf-8",
    )

    config = load_source_run_config(config_path)

    assert config.source_id == "pg-prod"
    assert config.context_root == "./organization_context"
    assert config.executor is not None
    assert config.executor.kind == "dbapi"
    assert config.executor.module == "tests.fake_dbapi_module"
