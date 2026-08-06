from pathlib import Path
import json
from app.phase3_retrieval import load_chunks, retrieve

ROOT = Path(__file__).resolve().parents[1]
KNOWLEDGE = ROOT / "data" / "phase3" / "knowledge"
OUT = ROOT / "artifacts" / "phase3" / "qwen_evaluation.json"
CASES = [
    {"id":"brake_001","question":"What should be checked when a brake fault is reported?","expected":"brake"},
    {"id":"warranty_001","question":"What should be reviewed before approving a repair for warranty coverage?","expected":"warranty"},
    {"id":"pm_001","question":"What maintenance requirements should be considered for scheduled PM?","expected":"maintenance"},
    {"id":"compliance_001","question":"What compliance requirements should be checked before return to service?","expected":"compliance"},
]

# This evaluator validates the evidence contract independently of model availability.
# Qwen is invoked only when requirements-ai.txt is installed and explicitly enabled.
results=[]
chunks=load_chunks(KNOWLEDGE)
for case in CASES:
    retrieved=retrieve(case["question"],chunks,top_k=3)
    evidence_ok=any(case["expected"] in r["chunk"].text.lower() for r in retrieved)
    results.append({"id":case["id"],"question":case["question"],"evidence_found":evidence_ok,"sources":[r["chunk"].document_id for r in retrieved]})

OUT.parent.mkdir(parents=True,exist_ok=True)
OUT.write_text(json.dumps(results,indent=2),encoding="utf-8")
failed=[r for r in results if not r["evidence_found"]]
print(f"Grounding evidence contract: {len(results)-len(failed)}/{len(results)}")
if failed: raise SystemExit(1)
