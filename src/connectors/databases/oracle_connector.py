from __future__ import annotations

from .base import DatabaseConnector


class OracleConnector(DatabaseConnector):
    """Starter Oracle connector scaffold."""

    platform_name = "Oracle"

    def discover_assets(self):
        raise NotImplementedError("Oracle discovery is not implemented yet.")

    def profile_asset(self, asset):
        raise NotImplementedError("Oracle profiling is not implemented yet.")

    def sample_asset(self, asset, limit: int = 5):
        raise NotImplementedError("Oracle sampling is not implemented yet.")

    def detect_changes(self):
        raise NotImplementedError("Oracle drift detection is not implemented yet.")
