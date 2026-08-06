from pathlib import Path
from app.phase3_retrieval import load_chunks, retrieve

ROOT = Path(__file__).resolve().parents[1]
KNOWLEDGE = ROOT / "data" / "phase3" / "knowledge"
CASES = [
    ("brake fault inspection procedure", "brake"),
    ("warranty coverage repair approval", "warranty"),
    ("maintenance PM interval requirements", "maintenance"),
    ("compliance inspection requirements", "compliance"),
    ("VMRS coding repair work order", "vmrs"),
]

chunks = load_chunks(KNOWLEDGE)
passed = 0
for query, expected in CASES:
    results = retrieve(query, chunks, top_k=3)
    ok = any(expected in r["chunk"].text.lower() for r in results)
    passed += int(ok)
    print(f"{'PASS' if ok else 'FAIL'} | {query}")

print(f"Retrieval evaluation: {passed}/{len(CASES)}")
if passed != len(CASES):
    raise SystemExit(1)
