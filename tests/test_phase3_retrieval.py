from pathlib import Path

from app.phase3_retrieval import load_chunks, retrieve

ROOT = Path(__file__).resolve().parents[1]
KNOWLEDGE = ROOT / "data" / "phase3" / "knowledge"


def test_knowledge_documents_are_loadable():
    chunks = load_chunks(KNOWLEDGE)
    assert len(chunks) >= 5
    assert all(c.document_id and c.text for c in chunks)


def test_fault_query_retrieves_relevant_knowledge():
    results = retrieve("brake fault inspection procedure", load_chunks(KNOWLEDGE))
    assert results
    assert any("brake" in r["chunk"].text.lower() for r in results)


def test_warranty_query_retrieves_warranty_policy():
    results = retrieve("warranty coverage repair approval", load_chunks(KNOWLEDGE))
    assert results
    assert any("warranty" in r["chunk"].text.lower() for r in results)
