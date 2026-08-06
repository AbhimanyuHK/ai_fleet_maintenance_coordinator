from pathlib import Path
from app.phase3_embeddings import build_index, search_index

ROOT = Path(__file__).resolve().parents[1]
KNOWLEDGE = ROOT / "data" / "phase3" / "knowledge"
INDEX = ROOT / "artifacts" / "phase3" / "vector_index"

CASES = [
    ("brake fault inspection procedure", "brake"),
    ("warranty coverage repair approval", "warranty"),
    ("maintenance PM interval requirements", "maintenance"),
    ("compliance inspection requirements", "compliance"),
    ("VMRS coding repair work order", "vmrs"),
]

build_index(KNOWLEDGE, INDEX)
passed = 0
for query, expected in CASES:
    results = search_index(INDEX, query, top_k=3)
    ok = any(expected in r["text"].lower() for r in results)
    passed += int(ok)
    print(f"{'PASS' if ok else 'FAIL'} | {query}")

print(f"BGE/FAISS retrieval evaluation: {passed}/{len(CASES)}")
if passed != len(CASES):
    raise SystemExit(1)
