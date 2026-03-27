import json

from models import SemanticLayerDraft
from semantic_layer import SemanticLayerRepository


def test_semantic_layer_repository_round_trips_empty_draft(tmp_path) -> None:
    repository = SemanticLayerRepository(tmp_path)
    draft = SemanticLayerDraft(version="draft-v1")

    saved_path = repository.save(draft)
    loaded = repository.load("draft-v1")

    assert saved_path.exists()
    assert loaded.version == "draft-v1"
    assert loaded.entities == []
    assert json.loads(saved_path.read_text(encoding="utf-8"))["version"] == "draft-v1"
