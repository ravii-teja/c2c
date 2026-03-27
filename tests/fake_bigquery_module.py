class FakeRow:
    def __init__(self, payload):
        self.payload = payload

    def items(self):
        return self.payload.items()


class Job:
    def __init__(self, query):
        self.query_text = " ".join(query.split())

    def result(self):
        if "region-us.INFORMATION_SCHEMA.SCHEMATA" in self.query_text:
            return [FakeRow({"schema_name": "analytics"})]
        if "`analytics`.INFORMATION_SCHEMA.COLUMNS" in self.query_text:
            return [
                FakeRow(
                    {
                        "table_schema": "analytics",
                        "table_name": "sessions",
                        "table_type": "BASE TABLE",
                        "column_name": "session_id",
                        "data_type": "INT64",
                        "is_nullable": "NO",
                    }
                ),
                FakeRow(
                    {
                        "table_schema": "analytics",
                        "table_name": "sessions",
                        "table_type": "BASE TABLE",
                        "column_name": "revenue_amount",
                        "data_type": "FLOAT64",
                        "is_nullable": "YES",
                    }
                ),
            ]
        if "CAST(NULL AS STRING) AS freshness_hint FROM `analytics.sessions`" in self.query_text:
            return [FakeRow({"row_count": 3, "freshness_hint": None})]
        if "SELECT * FROM `analytics.sessions` LIMIT 5" in self.query_text:
            return [
                FakeRow({"session_id": 1, "revenue_amount": 10.0}),
                FakeRow({"session_id": 2, "revenue_amount": 20.0}),
            ]
        raise AssertionError(f"Unexpected query: {self.query_text}")


class Client:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def query(self, query):
        return Job(query)
