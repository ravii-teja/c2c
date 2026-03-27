from __future__ import annotations

from .base import DatabaseConnector


class MySqlConnector(DatabaseConnector):
    """Starter MySQL connector scaffold."""

    platform_name = "MySQL"

    def discover_assets(self):
        raise NotImplementedError("MySQL discovery is not implemented yet.")

    def profile_asset(self, asset):
        raise NotImplementedError("MySQL profiling is not implemented yet.")

    def sample_asset(self, asset, limit: int = 5):
        raise NotImplementedError("MySQL sampling is not implemented yet.")

    def detect_changes(self):
        raise NotImplementedError("MySQL drift detection is not implemented yet.")
