from __future__ import annotations

from .base import DatabaseConnector


class RedshiftConnector(DatabaseConnector):
    """Starter Amazon Redshift connector scaffold."""

    platform_name = "Redshift"

    def discover_assets(self):
        raise NotImplementedError("Redshift discovery is not implemented yet.")

    def profile_asset(self, asset):
        raise NotImplementedError("Redshift profiling is not implemented yet.")

    def sample_asset(self, asset, limit: int = 5):
        raise NotImplementedError("Redshift sampling is not implemented yet.")

    def detect_changes(self):
        raise NotImplementedError("Redshift drift detection is not implemented yet.")
