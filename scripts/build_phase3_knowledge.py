from pathlib import Path
import sys
from app.knowledge_foundation import validate_registry, build_chunks

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "phase3"
OUTPUT = ROOT / "artifacts" / "phase3" / "knowledge_chunks.csv"

errors = validate_registry(DATA)
if errors:
    print("Knowledge registry validation failed:")
    print("\n".join(f"- {e}" for e in errors))
    sys.exit(1)

chunks = build_chunks(DATA, OUTPUT)
print(f"Validated knowledge registry and built {len(chunks)} chunks at {OUTPUT}")
