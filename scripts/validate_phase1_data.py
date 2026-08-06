from pathlib import Path

from app.data_quality import phase1_quality_report


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1] / "data" / "phase1"
    report = phase1_quality_report(root)
    print(report.to_string(index=False))
    failures = report.loc[~report["passed"]]
    print(f"\nChecks: {len(report)} | Failures: {len(failures)}")
    raise SystemExit(1 if not failures.empty else 0)
