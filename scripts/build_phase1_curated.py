from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "phase1"
CURATED = ROOT / "data" / "phase1_curated"


def load(name: str) -> pd.DataFrame:
    return pd.read_csv(RAW / f"{name}.csv")


def build_pm_due_queue() -> pd.DataFrame:
    pm = load("pm_schedule")
    pm["current_due_date"] = pd.to_datetime(pm["current_due_date"], errors="coerce")
    as_of = pd.Timestamp("2026-08-06")
    pm["days_to_due"] = (pm["current_due_date"] - as_of).dt.days
    pm["schedule_required"] = (
        pm["status"].isin(["OPEN", "OVERDUE"]) & (pm["days_to_due"] <= 5)
    )
    pm["pm_priority"] = "NONE"
    pm.loc[pm["days_to_due"] < 0, "pm_priority"] = "CRITICAL"
    pm.loc[(pm["days_to_due"] >= 0) & (pm["days_to_due"] <= 5), "pm_priority"] = "HIGH"
    return pm.sort_values(["schedule_required", "days_to_due"], ascending=[False, True])


def build_active_fault_queue() -> pd.DataFrame:
    faults = load("fault_events")
    active = faults[faults["active_flag"].astype(str).str.lower() == "true"].copy()
    active["priority"] = active["severity"].str.upper()
    active.loc[active["safety_related"].astype(str).str.lower() == "true", "priority"] = "CRITICAL"
    active.loc[(active["occurrence_count"] >= 3) & (active["priority"] == "MEDIUM"), "priority"] = "HIGH"
    rank = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    active["priority_rank"] = active["priority"].map(rank).fillna(9)
    return active.sort_values(["priority_rank", "occurrence_count"], ascending=[True, False])


def build_open_work_order_queue() -> pd.DataFrame:
    wo = load("work_orders")
    wo["opened_at"] = pd.to_datetime(wo["opened_at"], errors="coerce", utc=True)
    as_of = pd.Timestamp("2026-08-06T00:00:00Z")
    wo["age_days"] = (as_of - wo["opened_at"]).dt.days
    wo["aging_exception"] = (wo["status"].str.upper() == "OPEN") & (wo["age_days"] > 30)
    wo["priority_rank"] = wo["priority"].map({"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}).fillna(9)
    return wo[wo["status"].str.upper() == "OPEN"].sort_values(["priority_rank", "age_days"], ascending=[True, False])


def build_equipment_snapshot() -> pd.DataFrame:
    equipment = load("equipment_master")
    faults = load("fault_events")
    wo = load("work_orders")
    pm = load("pm_schedule")
    inspections = load("compliance_inspections")

    active_faults = faults[faults["active_flag"].astype(str).str.lower() == "true"].groupby("equipment_id").size().rename("active_fault_count")
    open_wo = wo[wo["status"].str.upper() == "OPEN"].groupby("equipment_id").size().rename("open_work_order_count")
    pm_open = pm[pm["status"].isin(["OPEN", "OVERDUE"])].groupby("equipment_id").size().rename("open_pm_count")
    failed = inspections[inspections["inspection_status"].str.upper() == "FAIL"].groupby("equipment_id").size().rename("failed_inspection_count")

    snapshot = equipment.merge(active_faults, on="equipment_id", how="left")
    snapshot = snapshot.merge(open_wo, on="equipment_id", how="left")
    snapshot = snapshot.merge(pm_open, on="equipment_id", how="left")
    snapshot = snapshot.merge(failed, on="equipment_id", how="left")
    for col in ["active_fault_count", "open_work_order_count", "open_pm_count", "failed_inspection_count"]:
        snapshot[col] = snapshot[col].fillna(0).astype(int)
    snapshot["attention_required"] = (
        (snapshot["active_fault_count"] > 0)
        | (snapshot["open_work_order_count"] > 0)
        | (snapshot["open_pm_count"] > 0)
        | (snapshot["failed_inspection_count"] > 0)
    )
    return snapshot


def main() -> None:
    CURATED.mkdir(parents=True, exist_ok=True)
    outputs = {
        "pm_due_queue": build_pm_due_queue(),
        "active_fault_queue": build_active_fault_queue(),
        "open_work_order_queue": build_open_work_order_queue(),
        "equipment_maintenance_snapshot": build_equipment_snapshot(),
    }
    for name, frame in outputs.items():
        frame.to_csv(CURATED / f"{name}.csv", index=False)
        print(f"wrote {name}: {len(frame)} rows")


if __name__ == "__main__":
    main()
