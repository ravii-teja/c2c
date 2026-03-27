from __future__ import annotations

from typing import Any, Protocol


QueryParams = dict[str, Any] | None
Row = dict[str, Any]


class QueryExecutor(Protocol):
    """Minimal execution protocol for database and warehouse connectors."""

    def fetch_all(self, query: str, params: QueryParams = None) -> list[Row]:
        """Return all rows for a read-only query."""


class DbApiQueryExecutor:
    """Adapter for Python DB-API compatible connections."""

    def __init__(self, connection: Any) -> None:
        self.connection = connection

    def fetch_all(self, query: str, params: QueryParams = None) -> list[Row]:
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, params or {})
            column_names = [description[0] for description in cursor.description or []]
            rows = cursor.fetchall()
        finally:
            cursor.close()

        return [dict(zip(column_names, row, strict=False)) for row in rows]


class BigQueryQueryExecutor:
    """
    Adapter for clients that expose a BigQuery-like `query(...).result()` API.

    This keeps the core package independent from the Google SDK while making the
    connector easy to wire into a real client later.
    """

    def __init__(self, client: Any) -> None:
        self.client = client

    def fetch_all(self, query: str, params: QueryParams = None) -> list[Row]:
        if params:
            raise ValueError("BigQueryQueryExecutor does not support named params yet.")

        query_job = self.client.query(query)
        results = query_job.result()
        return [dict(row.items()) for row in results]
