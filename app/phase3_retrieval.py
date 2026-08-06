from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Iterable


@dataclass(frozen=True)
class KnowledgeChunk:
    chunk_id: str
    document_id: str
    title: str
    source_type: str
    authority: str
    text: str


def _tokens(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def load_chunks(path: Path) -> list[KnowledgeChunk]:
    chunks: list[KnowledgeChunk] = []
    for file in sorted(path.glob("*.md")):
        text = file.read_text(encoding="utf-8")
        metadata: dict[str, str] = {}
        body: list[str] = []
        for line in text.splitlines():
            if line.startswith("# "):
                metadata["title"] = line[2:].strip()
            elif line.startswith("- ") and ":" in line:
                key, value = line[2:].split(":", 1)
                metadata[key.strip().lower().replace(" ", "_")] = value.strip()
            else:
                body.append(line)
        chunks.append(KnowledgeChunk(
            chunk_id=file.stem,
            document_id=metadata.get("document_id", file.stem),
            title=metadata.get("title", file.stem),
            source_type=metadata.get("source_type", "unknown"),
            authority=metadata.get("authority", "unknown"),
            text="\n".join(body).strip(),
        ))
    return chunks


def retrieve(query: str, chunks: Iterable[KnowledgeChunk], top_k: int = 3) -> list[dict]:
    q = _tokens(query)
    scored = []
    for chunk in chunks:
        tokens = _tokens(chunk.text + " " + chunk.title)
        overlap = len(q & tokens)
        if overlap:
            score = overlap / max(len(q), 1)
            scored.append({"chunk": chunk, "score": round(score, 4)})
    return sorted(scored, key=lambda x: x["score"], reverse=True)[:top_k]
