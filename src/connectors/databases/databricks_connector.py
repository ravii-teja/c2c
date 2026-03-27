from __future__ import annotations

from .base import DatabaseConnector


class DatabricksConnector(DatabaseConnector):
    """Starter Databricks connector scaffold."""

    platform_name = "Databricks"

    def discover_assets(self):
        raise NotImplementedError("Databricks discovery is not implemented yet.")

    def profile_asset(self, asset):
        raise NotImplementedError("Databricks profiling is not implemented yet.")

    def sample_asset(self, asset, limit: int = 5):
        raise NotImplementedError("Databricks sampling is not implemented yet.")

    def detect_changes(self):
        raise NotImplementedError("Databricks drift detection is not implemented yet.")
