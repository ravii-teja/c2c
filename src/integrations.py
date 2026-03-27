from __future__ import annotations

import importlib
from typing import Any

from config import ExecutorConfig
from connectors.databases import BigQueryQueryExecutor, DbApiQueryExecutor


def load_object(dotted_path: str) -> Any:
    module_name, object_name = dotted_path.rsplit(".", maxsplit=1)
    module = importlib.import_module(module_name)
    return getattr(module, object_name)


def build_executor_from_config(config: ExecutorConfig):
    if config.kind == "dbapi":
        if not config.module:
            raise ValueError("DB-API executor config requires 'module'.")
        module = importlib.import_module(config.module)
        connection = module.connect(*config.args, **config.kwargs)
        return DbApiQueryExecutor(connection)

    if config.kind == "bigquery_client":
        if config.factory:
            factory = load_object(config.factory)
            client = factory(*config.args, **config.kwargs)
            return BigQueryQueryExecutor(client)
        if config.module:
            module = importlib.import_module(config.module)
            client_factory = getattr(module, "Client")
            client = client_factory(*config.args, **config.kwargs)
            return BigQueryQueryExecutor(client)
        raise ValueError("BigQuery executor config requires 'factory' or 'module'.")

    raise ValueError(f"Unsupported executor kind: {config.kind}")
