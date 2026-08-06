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
    values = child[child_key].dropna().astype(str)
    failures = int((~values.isin(valid)).sum())
    return CheckResult(name, "reference", failures == 0, failures, "")


def date_order(df: pd.DataFrame, dataset: str, start: str, end: str) -> CheckResult:
    if start not in df.columns or end not in df.columns:
        return CheckResult(dataset, "date_order", True, 0, "Optional end field not present")
    s = pd.to_datetime(df[start], errors="coerce", utc=True)
    e = pd.to_datetime(df[end], errors="coerce", utc=True)
    failures = int((s.notna() & e.notna() & (e < s)).sum())
    return CheckResult(dataset, "date_order", failures == 0, failures, "")


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
        "equipment_master": ["equipment_id", "unit_number", "asset_type", "make", "model", "year", "status", "current_mileage", "engine_hours", "source_system", "source_record_id", "ingested_at"],
        "pm_schedule": ["pm_id", "equipment_id", "pm_type", "current_due_date", "status", "vendor_id", "location_id", "source_system", "source_record_id", "ingested_at"],
        "maintenance_history": ["history_id", "equipment_id", "service_date", "repair_category", "total_cost", "vendor_id"],
        "fault_events": ["fault_id", "equipment_id", "fault_code", "first_detected_at", "occurrence_count", "severity", "safety_related", "active_flag"],
        "work_orders": ["work_order_id", "equipment_id", "opened_at", "status", "priority", "vendor_id", "service_location_id", "estimated_cost", "approved_cost", "actual_cost"],
        "vendor_master": ["vendor_id", "vendor_name", "status", "preferred_flag"],
        "service_locations": ["location_id", "vendor_id", "active_flag", "preferred_flag"],
        "equipment_availability": ["availability_id", "equipment_id", "start_at", "end_at", "availability_status"],
        "campaigns": ["campaign_id", "oem", "campaign_number", "campaign_description", "status"],
        "compliance_inspections": ["inspection_id", "equipment_id", "inspection_type", "inspection_date", "inspection_status"],
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

    results += non_null(frames["equipment_master"], "equipment_master", ["equipment_id", "unit_number", "asset_type"])
    results += non_null(frames["pm_schedule"], "pm_schedule", ["pm_id", "equipment_id", "current_due_date"])
    results += non_negative(frames["equipment_master"], "equipment_master", ["current_mileage", "engine_hours"])
    results += non_negative(frames["work_orders"], "work_orders", ["estimated_cost", "approved_cost", "actual_cost"])
    results += non_negative(frames["maintenance_history"], "maintenance_history", ["parts_cost", "labor_cost", "total_cost"])

    results.append(reference_check(frames["pm_schedule"], frames["equipment_master"], "equipment_id", "equipment_id", "pm_to_equipment"))
    results.append(reference_check(frames["maintenance_history"], frames["equipment_master"], "equipment_id", "equipment_id", "history_to_equipment"))
    results.append(reference_check(frames["fault_events"], frames["equipment_master"], "equipment_id", "equipment_id", "fault_to_equipment"))
    results.append(reference_check(frames["work_orders"], frames["equipment_master"], "equipment_id", "equipment_id", "work_order_to_equipment"))
    results.append(reference_check(frames["equipment_availability"], frames["equipment_master"], "equipment_id", "equipment_id", "availability_to_equipment"))
    results.append(reference_check(frames["compliance_inspections"], frames["equipment_master"], "equipment_id", "equipment_id", "inspection_to_equipment"))
    results.append(reference_check(frames["pm_schedule"], frames["vendor_master"], "vendor_id", "vendor_id", "pm_to_vendor"))
    results.append(reference_check(frames["work_orders"], frames["vendor_master"], "vendor_id", "vendor_id", "work_order_to_vendor"))
    results.append(reference_check(frames["service_locations"], frames["vendor_master"], "vendor_id", "vendor_id", "location_to_vendor"))
    results.append(reference_check(frames["pm_schedule"], frames["service_locations"], "location_id", "location_id", "pm_to_location"))
    results.append(reference_check(frames["work_orders"], frames["service_locations"], "service_location_id", "location_id", "work_order_to_location"))

    results.append(date_order(frames["work_orders"], "work_orders", "opened_at", "closed_at"))
    results.append(date_order(frames["equipment_availability"], "equipment_availability", "start_at", "end_at"))

    return pd.DataFrame([r.__dict__ for r in results])
