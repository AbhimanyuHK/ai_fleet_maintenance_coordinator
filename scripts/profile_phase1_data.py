from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "phase1"
REPORTS = ROOT / "reports"

FILES = sorted(DATA.glob("*.csv"))


def main() -> None:
    REPORTS.mkdir(exist_ok=True)
    rows = []
    for path in FILES:
        df = pd.read_csv(path)
        rows.append({
            "dataset": path.stem,
            "rows": len(df),
            "columns": len(df.columns),
            "null_cells": int(df.isna().sum().sum()),
            "duplicate_rows": int(df.duplicated().sum()),
            "memory_bytes": int(df.memory_usage(deep=True).sum()),
        })
    profile = pd.DataFrame(rows)
    profile.to_csv(REPORTS / "phase1_data_profile.csv", index=False)
    print(profile.to_string(index=False))


if __name__ == "__main__":
    main()
