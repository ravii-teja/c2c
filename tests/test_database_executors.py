from __future__ import annotations

from connectors.databases import BigQueryQueryExecutor, DbApiQueryExecutor


class FakeCursor:
    def __init__(self) -> None:
        self.description = [("id",), ("name",)]
        self.executed: list[tuple[str, dict]] = []

    def execute(self, query: str, params: dict) -> None:
        self.executed.append((query, params))

    def fetchall(self):
        return [(1, "alpha"), (2, "beta")]

    def close(self) -> None:
        return None


class FakeConnection:
    def __init__(self) -> None:
        self.cursor_instance = FakeCursor()

    def cursor(self) -> FakeCursor:
        return self.cursor_instance


class FakeBigQueryRow:
    def __init__(self, payload: dict) -> None:
        self.payload = payload

    def items(self):
        return self.payload.items()


class FakeBigQueryJob:
    def result(self):
        return [FakeBigQueryRow({"id": 1}), FakeBigQueryRow({"id": 2})]


class FakeBigQueryClient:
    def __init__(self) -> None:
        self.queries: list[str] = []

    def query(self, query: str) -> FakeBigQueryJob:
        self.queries.append(query)
        return FakeBigQueryJob()


def test_dbapi_query_executor_returns_dict_rows() -> None:
    executor = DbApiQueryExecutor(FakeConnection())

    rows = executor.fetch_all("SELECT id, name FROM test", {"limit": 2})

    assert rows == [{"id": 1, "name": "alpha"}, {"id": 2, "name": "beta"}]


def test_bigquery_query_executor_returns_dict_rows() -> None:
    client = FakeBigQueryClient()
    executor = BigQueryQueryExecutor(client)

    rows = executor.fetch_all("SELECT id FROM dataset.table")

    assert rows == [{"id": 1}, {"id": 2}]
    assert client.queries == ["SELECT id FROM dataset.table"]
