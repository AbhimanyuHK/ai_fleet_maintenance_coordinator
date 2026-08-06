from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "phase1"
STANDARDIZED = ROOT / "data" / "phase1_standardized"

DATE_COLUMNS = {
    "equipment_master": ["in_service_date", "ingested_at"],
    "pm_schedule": ["last_service_date", "current_due_date", "scheduled_date", "ingested_at"],
    "maintenance_history": ["service_date"],
    "fault_events": ["first_detected_at", "last_detected_at"],
    "work_orders": ["opened_at", "completion_at", "last_updated_at", "closed_at"],
    "equipment_availability": ["start_at", "end_at"],
    "compliance_inspections": ["inspection_date", "resolved_at"],
}

BOOLEAN_COLUMNS = {
    "equipment_master": [],
    "pm_schedule": ["required_by_oem", "required_by_company_policy"],
    "maintenance_history": ["warranty_flag", "repeat_repair_flag"],
    "fault_events": ["safety_related", "compliance_related", "active_flag"],
    "work_orders": ["approval_status", "safety_hold", "compliance_hold"],
    "vendor_master": ["preferred_flag", "national_account_flag", "warranty_capability"],
    "service_locations": ["preferred_flag", "active_flag"],
    "equipment_availability": ["planned_dispatch", "planned_downtime"],
    "campaigns": [],
    "compliance_inspections": ["safety_related", "compliance_related", "corrective_action_required"],
}


def normalize_bool(series: pd.Series) -> pd.Series:
    mapping = {"true": True, "false": False, "1": True, "0": False, "yes": True, "no": False}
    return series.astype(str).str.strip().str.lower().map(mapping)


def main() -> None:
    STANDARDIZED.mkdir(parents=True, exist_ok=True)
    for path in sorted(RAW.glob("*.csv")):
        name = path.stem
        df = pd.read_csv(path)
        for col in DATE_COLUMNS.get(name, []):
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce", utc=True)
        for col in BOOLEAN_COLUMNS.get(name, []):
            if col in df.columns and col not in {"approval_status"}:
                df[col] = normalize_bool(df[col])
        df.columns = [c.strip().lower() for c in df.columns]
        df.to_csv(STANDARDIZED / path.name, index=False)
        print(f"standardized {name}: {len(df)} rows")


if __name__ == "__main__":
    main()
