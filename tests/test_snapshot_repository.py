from connectors.databases import SchemaSnapshot
from discovery import SchemaSnapshotRepository


def test_snapshot_repository_round_trips_snapshot(tmp_path) -> None:
    repository = SchemaSnapshotRepository(tmp_path)
    snapshot = SchemaSnapshot(
        source_id="src-1",
        captured_at=__import__("datetime").datetime.fromisoformat("2026-03-23T12:00:00+00:00"),
        asset_signatures={"src-1:public.orders": "abc123"},
    )

    saved_path = repository.save_latest(snapshot)
    loaded = repository.load_latest("src-1")

    assert saved_path.exists()
    assert loaded is not None
    assert loaded.source_id == "src-1"
    assert loaded.asset_signatures["src-1:public.orders"] == "abc123"
