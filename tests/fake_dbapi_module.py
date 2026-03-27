class Cursor:
    def __init__(self) -> None:
        self.description = []
        self._rows = []

    def execute(self, query, params):
        normalized = " ".join(query.split())
        if "FROM information_schema.columns" in normalized:
            self.description = [
                ("table_schema",),
                ("table_name",),
                ("table_type",),
                ("column_name",),
                ("data_type",),
                ("is_nullable",),
            ]
            self._rows = [
                ("public", "orders", "BASE TABLE", "order_id", "bigint", "NO"),
                ("public", "orders", "BASE TABLE", "total_amount", "numeric", "YES"),
            ]
        elif 'SELECT COUNT(*) AS row_count, NULL::text AS freshness_hint FROM "public"."orders"' in normalized:
            self.description = [("row_count",), ("freshness_hint",)]
            self._rows = [(2, None)]
        elif 'SELECT * FROM "public"."orders" LIMIT 5' in normalized:
            self.description = [("order_id",), ("total_amount",)]
            self._rows = [(1, 10.5), (2, 20.0)]
        else:
            raise AssertionError(f"Unexpected query: {normalized}")

    def fetchall(self):
        return self._rows

    def close(self):
        return None


class Connection:
    def cursor(self):
        return Cursor()


def connect(*args, **kwargs):
    return Connection()
