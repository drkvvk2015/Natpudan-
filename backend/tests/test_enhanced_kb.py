"""Smoke tests for the enhanced knowledge base."""

from app.services import enhanced_knowledge_base as kb_module


def test_get_knowledge_base_returns_singleton(monkeypatch):
    monkeypatch.setattr(kb_module, "SENTENCE_TRANSFORMERS_AVAILABLE", False)
    monkeypatch.setattr(kb_module, "_knowledge_base_instance", None)

    first = kb_module.get_knowledge_base()
    second = kb_module.get_knowledge_base()

    assert first is second
    assert first.get_statistics()["sources"] >= 1


def test_enhanced_knowledge_base_search_returns_results(monkeypatch, tmp_path):
    monkeypatch.setattr(kb_module, "SENTENCE_TRANSFORMERS_AVAILABLE", False)

    kb = kb_module.EnhancedKnowledgeBase(storage_dir=str(tmp_path / "kb"))

    results = kb.search("high blood pressure symptoms", top_k=2)

    assert results
    assert any(result.get("icd10") == "I10" for result in results)
    assert all(result.get("score", 0) > 0 for result in results)
