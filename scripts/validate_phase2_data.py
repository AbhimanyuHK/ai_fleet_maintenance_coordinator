from pathlib import Path
import sys
from app.phase2_data_quality import quality_report, reconcile_estimates_invoices, build_review_queue

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "phase2"
OUT = ROOT / "reports" / "phase2"
OUT.mkdir(parents=True, exist_ok=True)

report = quality_report(DATA)
report.to_csv(OUT / "data_quality_report.csv", index=False)
reconcile_estimates_invoices(DATA).to_csv(OUT / "estimate_invoice_reconciliation.csv", index=False)
build_review_queue(DATA).to_csv(OUT / "human_review_queue.csv", index=False)

failed = report[(~report["passed"]) & (report["severity"] == "ERROR")]
print(report.to_string(index=False))
print(f"\nERROR checks: {len(failed)}")
if not failed.empty:
    sys.exit(1)
