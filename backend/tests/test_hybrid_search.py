from app.services.hybrid_search import HybridSearchEngine


def test_hybrid_search_returns_vector_fallback_when_bm25_unavailable():
    engine = HybridSearchEngine()
    vector_results = [
        {"content": "A", "metadata": {"document_id": "d1"}},
        {"content": "B", "metadata": {"document_id": "d2"}},
    ]

    results = engine.hybrid_search("query", vector_results, top_k=1)
    assert len(results) == 1
    assert results[0]["metadata"]["document_id"] == "d1"


def test_tokenize_splits_on_punctuation():
    engine = HybridSearchEngine()
    tokens = engine._tokenize("Blood-pressure, diabetes!")
    assert "blood" in tokens
    assert "pressure" in tokens
    assert "diabetes" in tokens
