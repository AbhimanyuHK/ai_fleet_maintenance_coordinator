from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import pandas as pd


@dataclass
class CheckResult:
    dataset: str
    check: str
    passed: bool
    failures: int
    detail: str


def load_csv(path: str | Path) -> pd.DataFrame:
    return pd.read_csv(path)


def required_columns(df: pd.DataFrame, dataset: str, columns: Iterable[str]) -> list[CheckResult]:
    missing = [c for c in columns if c not in df.columns]
    return [CheckResult(dataset, "required_columns", not missing, len(missing), f"Missing: {missing}")]


def non_null(df: pd.DataFrame, dataset: str, columns: Iterable[str]) -> list[CheckResult]:
    results = []
    for column in columns:
        if column not in df.columns:
            results.append(CheckResult(dataset, f"non_null:{column}", False, 1, "Column missing"))
            continue
        failures = int(df[column].isna().sum())
        results.append(CheckResult(dataset, f"non_null:{column}", failures == 0, failures, ""))
    return results


def non_negative(df: pd.DataFrame, dataset: str, columns: Iterable[str]) -> list[CheckResult]:
    results = []
    for column in columns:
        if column not in df.columns:
            continue
        numeric = pd.to_numeric(df[column], errors="coerce")
        failures = int((numeric.dropna() < 0).sum())
        results.append(CheckResult(dataset, f"non_negative:{column}", failures == 0, failures, ""))
    return results


def unique_key(df: pd.DataFrame, dataset: str, column: str) -> CheckResult:
    if column not in df.columns:
        return CheckResult(dataset, f"unique:{column}", False, 1, "Column missing")
    duplicates = int(df[column].duplicated(keep=False).sum())
    return CheckResult(dataset, f"unique:{column}", duplicates == 0, duplicates, "")


def reference_check(child: pd.DataFrame, parent: pd.DataFrame, child_key: str, parent_key: str, name: str) -> CheckResult:
    if child_key not in child.columns or parent_key not in parent.columns:
        return CheckResult(name, "reference", False, 1, "Reference column missing")
    valid = set(parent[parent_key].dropna().astype(str))
    failures = int((~child[child_key].dropna().astype(str).isin(valid)).sum())
    return CheckResult(name, "reference", failures == 0, failures, "")


def phase1_quality_report(data_dir: str | Path) -> pd.DataFrame:
    root = Path(data_dir)
    files = {
        "equipment_master": "equipment_master.csv",
        "pm_schedule": "pm_schedule.csv",
        "maintenance_history": "maintenance_history.csv",
        "fault_events": "fault_events.csv",
        "work_orders": "work_orders.csv",
        "vendor_master": "vendor_master.csv",
        "service_locations": "service_locations.csv",
        "equipment_availability": "equipment_availability.csv",
        "campaigns": "campaigns.csv",
        "compliance_inspections": "compliance_inspections.csv",
    }
    frames = {name: load_csv(root / filename) for name, filename in files.items()}
    results: list[CheckResult] = []

    contracts = {
        "equipment_master": ["equipment_id", "unit_number", "status"],
        "pm_schedule": ["pm_id", "equipment_id", "current_due_date", "status"],
        "maintenance_history": ["history_id", "equipment_id", "service_date"],
        "fault_events": ["fault_id", "equipment_id", "fault_code", "first_detected_at"],
        "work_orders": ["work_order_id", "equipment_id", "opened_at", "status"],
        "vendor_master": ["vendor_id", "vendor_name", "status"],
        "service_locations": ["location_id", "vendor_id", "active_flag"],
        "equipment_availability": ["availability_id", "equipment_id", "start_at", "end_at"],
        "campaigns": ["campaign_id", "oem", "campaign_number"],
        "compliance_inspections": ["inspection_id", "equipment_id", "inspection_date"],
    }
    keys = {
        "equipment_master": "equipment_id", "pm_schedule": "pm_id", "maintenance_history": "history_id",
        "fault_events": "fault_id", "work_orders": "work_order_id", "vendor_master": "vendor_id",
        "service_locations": "location_id", "equipment_availability": "availability_id",
        "campaigns": "campaign_id", "compliance_inspections": "inspection_id",
    }
    for name, columns in contracts.items():
        results += required_columns(frames[name], name, columns)
        results.append(unique_key(frames[name], name, keys[name]))

    results += non_null(frames["equipment_master"], "equipment_master", ["equipment_id", "unit_number"])
    results += non_null(frames["pm_schedule"], "pm_schedule", ["pm_id", "equipment_id", "current_due_date"])
    results += non_negative(frames["equipment_master"], "equipment_master", ["current_mileage", "engine_hours"])
    results += non_negative(frames["work_orders"], "work_orders", ["estimated_cost", "approved_cost", "actual_cost"])
    results.append(reference_check(frames["pm_schedule"], frames["equipment_master"], "equipment_id", "equipment_id", "pm_to_equipment"))
    results.append(reference_check(frames["fault_events"], frames["equipment_master"], "equipment_id", "equipment_id", "fault_to_equipment"))
    results.append(reference_check(frames["work_orders"], frames["equipment_master"], "equipment_id", "equipment_id", "work_order_to_equipment"))
    results.append(reference_check(frames["work_orders"], frames["vendor_master"], "vendor_id", "vendor_id", "work_order_to_vendor"))
    results.append(reference_check(frames["service_locations"], frames["vendor_master"], "vendor_id", "vendor_id", "location_to_vendor"))
    return pd.DataFrame([r.__dict__ for r in results])
