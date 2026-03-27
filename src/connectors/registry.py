from __future__ import annotations

from collections.abc import Iterable

from .base import Connector


class ConnectorRegistry:
    """In-memory registry for active connectors."""

    def __init__(self) -> None:
        self._connectors: dict[str, Connector] = {}

    def register(self, connector: Connector) -> None:
        self._connectors[connector.source.source_id] = connector

    def get(self, source_id: str) -> Connector:
        return self._connectors[source_id]

    def list(self) -> list[Connector]:
        return list(self._connectors.values())

    def extend(self, connectors: Iterable[Connector]) -> None:
        for connector in connectors:
            self.register(connector)
