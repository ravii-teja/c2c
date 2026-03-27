from __future__ import annotations

from .base import DatabaseConnector


class SqlServerConnector(DatabaseConnector):
    """Starter SQL Server connector scaffold."""

    platform_name = "SQL Server"

    def discover_assets(self):
        raise NotImplementedError("SQL Server discovery is not implemented yet.")

    def profile_asset(self, asset):
        raise NotImplementedError("SQL Server profiling is not implemented yet.")

    def sample_asset(self, asset, limit: int = 5):
        raise NotImplementedError("SQL Server sampling is not implemented yet.")

    def detect_changes(self):
        raise NotImplementedError("SQL Server drift detection is not implemented yet.")
