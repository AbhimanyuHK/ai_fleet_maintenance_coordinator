from __future__ import annotations

from pathlib import Path
import hashlib
import re
import pandas as pd

REQUIRED_SOURCE_COLUMNS = ["source_id","source_type","source_name","authority_level","owner","effective_date","version","status","scope"]
REQUIRED_DOCUMENT_COLUMNS = ["document_id","source_id","document_name","document_type","version","effective_date","status","language","file_path","content_hash","approved_for_rag"]


def load_registry(root: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    return (
        pd.read_csv(root / "knowledge_sources.csv"),
        pd.read_csv(root / "knowledge_documents.csv"),
    )


def validate_registry(root: Path) -> list[str]:
    sources, docs = load_registry(root)
    errors: list[str] = []
    for name, df, required, key in [
        ("knowledge_sources", sources, REQUIRED_SOURCE_COLUMNS, "source_id"),
        ("knowledge_documents", docs, REQUIRED_DOCUMENT_COLUMNS, "document_id"),
    ]:
        missing = [c for c in required if c not in df.columns]
        if missing:
            errors.append(f"{name}: missing columns {missing}")
            continue
        if df[key].duplicated().any(): errors.append(f"{name}: duplicate {key}")
        if df[required].isna().any().any(): errors.append(f"{name}: required values contain nulls")
    if not set(docs["source_id"]).issubset(set(sources["source_id"])):
        errors.append("knowledge_documents: unresolved source_id")
    if not docs["status"].astype(str).str.upper().eq("APPROVED").all():
        errors.append("knowledge_documents: unapproved documents registered")
    if not docs["approved_for_rag"].astype(str).str.lower().eq("true").all():
        errors.append("knowledge_documents: documents not approved for RAG")
    return errors


def normalize_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def chunk_text(text: str, max_chars: int = 700, overlap: int = 100) -> list[str]:
    if max_chars <= overlap: raise ValueError("max_chars must be greater than overlap")
    paragraphs = [p.strip() for p in normalize_text(text).split("\n\n") if p.strip()]
    chunks: list[str] = []
    current = ""
    for paragraph in paragraphs:
        candidate = paragraph if not current else current + "\n\n" + paragraph
        if len(candidate) <= max_chars:
            current = candidate
            continue
        if current: chunks.append(current)
        if len(paragraph) <= max_chars:
            tail = current[-overlap:] if current else ""
            current = (tail + "\n\n" + paragraph).strip() if tail else paragraph
        else:
            start = 0
            while start < len(paragraph):
                end = min(start + max_chars, len(paragraph))
                chunks.append(paragraph[start:end].strip())
                if end == len(paragraph): break
                start = end - overlap
            current = ""
    if current: chunks.append(current)
    return chunks


def build_chunks(root: Path, output: Path) -> pd.DataFrame:
    sources, docs = load_registry(root)
    source_map = sources.set_index("source_id").to_dict("index")
    rows = []
    for _, doc in docs.iterrows():
        if str(doc["approved_for_rag"]).lower() != "true": continue
        path = Path(doc["file_path"])
        if not path.is_absolute(): path = root.parent.parent / path
        text = normalize_text(path.read_text(encoding="utf-8"))
        for idx, chunk in enumerate(chunk_text(text), start=1):
            rows.append({
                "chunk_id": f"{doc['document_id']}-CH{idx:03d}",
                "document_id": doc["document_id"],
                "source_id": doc["source_id"],
                "source_type": source_map[doc["source_id"]]["source_type"],
                "authority_level": source_map[doc["source_id"]]["authority_level"],
                "document_version": doc["version"],
                "effective_date": doc["effective_date"],
                "chunk_index": idx,
                "text": chunk,
                "text_hash": hashlib.sha256(chunk.encode("utf-8")).hexdigest(),
            })
    result = pd.DataFrame(rows)
    output.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(output, index=False)
    return result
