from __future__ import annotations

from pathlib import Path

import pandas as pd

from app.data_quality import phase1_quality_report


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "phase1"
REPORTS = ROOT / "reports"


def main() -> None:
    REPORTS.mkdir(exist_ok=True)
    report = phase1_quality_report(DATA)
    report.to_csv(REPORTS / "phase1_data_quality.csv", index=False)

    total = len(report)
    passed = int(report["passed"].sum())
    failed = total - passed
    score = round((passed / total) * 100, 2) if total else 0.0

    readiness = "READY" if failed == 0 else "NOT_READY"
    summary = pd.DataFrame([{
        "readiness": readiness,
        "quality_score_percent": score,
        "checks": total,
        "passed": passed,
        "failed": failed,
    }])
    summary.to_csv(REPORTS / "phase1_readiness.csv", index=False)
    print(summary.to_string(index=False))

    if readiness != "READY":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
