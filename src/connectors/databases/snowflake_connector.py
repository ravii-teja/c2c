from __future__ import annotations

from .base import DatabaseConnector


class SnowflakeConnector(DatabaseConnector):
    """Starter Snowflake connector scaffold."""

    platform_name = "Snowflake"

    def discover_assets(self):
        raise NotImplementedError("Snowflake discovery is not implemented yet.")

    def profile_asset(self, asset):
        raise NotImplementedError("Snowflake profiling is not implemented yet.")

    def sample_asset(self, asset, limit: int = 5):
        raise NotImplementedError("Snowflake sampling is not implemented yet.")

    def detect_changes(self):
        raise NotImplementedError("Snowflake drift detection is not implemented yet.")
