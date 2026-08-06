from __future__ import annotations

from pathlib import Path
import json

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from app.phase3_retrieval import load_chunks

MODEL_NAME = "BAAI/bge-small-en-v1.5"


def build_index(knowledge_dir: Path, output_dir: Path, model_name: str = MODEL_NAME) -> dict:
    chunks = load_chunks(knowledge_dir)
    if not chunks:
        raise ValueError("No knowledge chunks found")
    model = SentenceTransformer(model_name)
    texts = [f"{c.title}\n{c.text}" for c in chunks]
    vectors = model.encode(texts, normalize_embeddings=True, convert_to_numpy=True, show_progress_bar=False)
    vectors = np.asarray(vectors, dtype="float32")
    index = faiss.IndexFlatIP(vectors.shape[1])
    index.add(vectors)
    output_dir.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(output_dir / "knowledge.faiss"))
    (output_dir / "metadata.json").write_text(json.dumps([
        {"chunk_id": c.chunk_id, "document_id": c.document_id, "title": c.title,
         "source_type": c.source_type, "authority": c.authority, "text": c.text}
        for c in chunks
    ], indent=2), encoding="utf-8")
    return {"model": model_name, "documents": len(chunks), "dimensions": int(vectors.shape[1])}
