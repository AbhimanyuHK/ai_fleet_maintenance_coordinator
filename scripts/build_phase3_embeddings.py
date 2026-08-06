from pathlib import Path
from app.phase3_embeddings import build_index

ROOT = Path(__file__).resolve().parents[1]
result = build_index(ROOT / "data" / "phase3" / "knowledge", ROOT / "artifacts" / "phase3" / "vector_index")
print(result)
