from pathlib import Path
import pandas as pd
from app.knowledge_foundation import validate_registry, chunk_text, build_chunks

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "phase3"


def test_knowledge_registry_is_valid():
    assert validate_registry(DATA) == []


def test_chunking_is_deterministic_and_bounded():
    text = "Paragraph one.\n\nParagraph two.\n\nParagraph three."
    chunks = chunk_text(text, max_chars=30, overlap=5)
    assert chunks
    assert all(len(c) <= 30 for c in chunks)
    assert chunk_text(text, max_chars=30, overlap=5) == chunks


def test_build_chunks_preserves_source_lineage(tmp_path):
    output = tmp_path / "chunks.csv"
    result = build_chunks(DATA, output)
    assert len(result) > 0
    assert set(["chunk_id","document_id","source_id","authority_level","document_version","text","text_hash"]).issubset(result.columns)
    assert result["chunk_id"].is_unique
    assert result["text_hash"].notna().all()
    assert output.exists()
