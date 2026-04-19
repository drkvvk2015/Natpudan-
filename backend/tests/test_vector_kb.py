from app.services.vector_knowledge_base import VectorKnowledgeBase


def test_chunk_text_single_chunk_when_short_text(tmp_path):
    kb = VectorKnowledgeBase(storage_dir=str(tmp_path / "kb"))
    chunks = kb._chunk_text("short text", chunk_size=100)
    assert chunks == ["short text"]


def test_search_keyword_fallback_uses_in_memory_documents(tmp_path):
    kb = VectorKnowledgeBase(storage_dir=str(tmp_path / "kb"))
    kb.documents = [
        {"chunk_text": "Patient has chest pain", "document_id": "1", "filename": "a.txt"},
        {"chunk_text": "General wellness and diet", "document_id": "2", "filename": "b.txt"},
    ]
    kb.index = None
    kb.openai_client = None

    results = kb.search("chest pain", top_k=2)
    assert results
    assert "chest pain" in results[0]["content"].lower()
