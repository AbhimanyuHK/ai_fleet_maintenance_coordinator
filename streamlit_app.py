from pathlib import Path

import pandas as pd
import streamlit as st

from app.phase2_data_quality import build_review_queue, reconcile_estimates_invoices

ROOT = Path(__file__).resolve().parent
PHASE1_DIR = ROOT / "data" / "phase1"
PHASE2_DIR = ROOT / "data" / "phase2"

PHASE1_DATASETS = {
    "Equipment Master": "equipment_master.csv",
    "PM Schedule": "pm_schedule.csv",
    "Maintenance History": "maintenance_history.csv",
    "Fault Events": "fault_events.csv",
    "Work Orders": "work_orders.csv",
    "Vendor Master": "vendor_master.csv",
    "Service Locations": "service_locations.csv",
    "Equipment Availability": "equipment_availability.csv",
    "Campaigns / Recalls": "campaigns.csv",
    "Compliance Inspections": "compliance_inspections.csv",
}
PHASE2_DATASETS = {
    "Communication Messages": "communication_messages.csv",
    "Communication Participants": "communication_participants.csv",
    "Voicemails": "voicemail_records.csv",
    "Driver Requests": "driver_requests.csv",
    "Vendor Estimates": "vendor_estimates.csv",
    "Estimate Lines": "vendor_estimate_lines.csv",
    "Vendor Invoices": "vendor_invoices.csv",
    "Invoice Lines": "vendor_invoice_lines.csv",
    "Repair Notes": "repair_notes.csv",
    "Document Artifacts": "document_artifacts.csv",
    "Human Review Tasks": "human_review_tasks.csv",
}

st.set_page_config(page_title="Fleet Maintenance Control Tower", page_icon="🚛", layout="wide")

st.title("🚛 Fleet Maintenance Control Tower")
st.caption("Maintenance operations, safety, repair, vendor and compliance intelligence")

@st.cache_data
def load_csv(directory: Path, filename: str) -> pd.DataFrame:
    return pd.read_csv(directory / filename)


def load_group(directory: Path, datasets: dict[str, str]) -> dict[str, pd.DataFrame]:
    return {name: load_csv(directory, filename) for name, filename in datasets.items() if (directory / filename).exists()}

p1 = load_group(PHASE1_DIR, PHASE1_DATASETS)
p2 = load_group(PHASE2_DIR, PHASE2_DATASETS)

# Common frames
fleet = p1.get("Equipment Master", pd.DataFrame())
pm = p1.get("PM Schedule", pd.DataFrame())
faults = p1.get("Fault Events", pd.DataFrame())
work_orders = p1.get("Work Orders", pd.DataFrame())
vendors = p1.get("Vendor Master", pd.DataFrame())
availability = p1.get("Equipment Availability", pd.DataFrame())
campaigns = p1.get("Campaigns / Recalls", pd.DataFrame())
compliance = p1.get("Compliance Inspections", pd.DataFrame())
requests = p2.get("Driver Requests", pd.DataFrame())
messages = p2.get("Communication Messages", pd.DataFrame())
voicemails = p2.get("Voicemails", pd.DataFrame())
estimates = p2.get("Vendor Estimates", pd.DataFrame())
invoices = p2.get("Vendor Invoices", pd.DataFrame())
repair_notes = p2.get("Repair Notes", pd.DataFrame())


def count_open(df: pd.DataFrame) -> int:
    return int((df["status"].astype(str).str.upper() == "OPEN").sum()) if "status" in df else 0


def show_table(df: pd.DataFrame, search_key: str, height: int = 420) -> None:
    if df.empty:
        st.info("No data available for this view.")
        return
    query = st.text_input("Search", key=search_key, placeholder="Search equipment, vendor, work order, status...")
    view = df.copy()
    if query.strip():
        mask = view.astype(str).apply(lambda col: col.str.contains(query, case=False, na=False)).any(axis=1)
        view = view[mask]
    st.dataframe(view, use_container_width=True, height=height, hide_index=True)


def metric(label: str, value: int | str) -> None:
    st.metric(label, value)

st.divider()
tabs = st.tabs([
    "Fleet Overview",
    "PM Management",
    "Faults & Alerts",
    "Work Orders & Repairs",
    "Driver Requests",
    "Vendor Management",
    "Estimates & Invoices",
    "Compliance & Campaigns",
    "Data Quality",
])

with tabs[0]:
    st.header("Fleet Overview")
    c = st.columns(6)
    c[0].metric("Equipment", len(fleet))
    c[1].metric("PM Records", len(pm))
    c[2].metric("Fault Events", len(faults))
    c[3].metric("Open Work Orders", count_open(work_orders))
    c[4].metric("Driver Requests", len(requests))
    c[5].metric("Review Items", len(build_review_queue(PHASE2_DIR)))
    left, right = st.columns(2)
    with left:
        st.subheader("PM Status")
        if not pm.empty and "status" in pm:
            st.bar_chart(pm["status"].value_counts())
    with right:
        st.subheader("Fault Severity")
        if not faults.empty and "severity" in faults:
            st.bar_chart(faults["severity"].value_counts())

with tabs[1]:
    st.header("PM Management")
    if not pm.empty:
        c = st.columns(3)
        c[0].metric("Scheduled PM", len(pm))
        c[1].metric("Due / Upcoming", int(pm["status"].astype(str).str.upper().isin(["DUE", "UPCOMING", "DUE_SOON"]).sum()) if "status" in pm else 0)
        c[2].metric("Overdue", int(pm["status"].astype(str).str.upper().eq("OVERDUE").sum()) if "status" in pm else 0)
    show_table(pm, "pm_search")

with tabs[2]:
    st.header("Faults & Alerts")
    if not faults.empty:
        c = st.columns(4)
        c[0].metric("Total Faults", len(faults))
        c[1].metric("Critical", int(faults["severity"].astype(str).str.upper().eq("CRITICAL").sum()) if "severity" in faults else 0)
        c[2].metric("High", int(faults["severity"].astype(str).str.upper().eq("HIGH").sum()) if "severity" in faults else 0)
        c[3].metric("Safety Related", int(faults["safety_related"].astype(str).str.lower().eq("true").sum()) if "safety_related" in faults else 0)
    show_table(faults, "fault_search")

with tabs[3]:
    st.header("Work Orders & Repairs")
    c = st.columns(4)
    c[0].metric("Work Orders", len(work_orders))
    c[1].metric("Open", count_open(work_orders))
    c[2].metric("Repair Notes", len(repair_notes))
    c[3].metric("Unavailable Fleet", int((availability["status"].astype(str).str.upper() != "AVAILABLE").sum()) if "status" in availability else 0)
    show_table(work_orders, "work_order_search")
    st.subheader("Repair Notes")
    show_table(repair_notes, "repair_note_search", 300)

with tabs[4]:
    st.header("Driver Requests")
    c = st.columns(4)
    c[0].metric("Requests", len(requests))
    c[1].metric("Safety Related", int(requests["safety_related"].astype(str).str.lower().eq("true").sum()) if "safety_related" in requests else 0)
    c[2].metric("Voicemails", len(voicemails))
    c[3].metric("Messages", len(messages))
    st.subheader("Requests")
    show_table(requests, "driver_request_search")
    st.subheader("Voicemails")
    show_table(voicemails, "voicemail_search", 300)
    st.subheader("Communication Messages")
    show_table(messages, "message_search", 300)

with tabs[5]:
    st.header("Vendor Management")
    c = st.columns(3)
    c[0].metric("Vendors", len(vendors))
    c[1].metric("Service Locations", len(p1.get("Service Locations", pd.DataFrame())))
    c[2].metric("Vendor Estimates", len(estimates))
    show_table(vendors, "vendor_search")
    st.subheader("Preferred / Service Locations")
    show_table(p1.get("Service Locations", pd.DataFrame()), "location_search", 300)

with tabs[6]:
    st.header("Estimates & Invoices")
    reconciliation = reconcile_estimates_invoices(PHASE2_DIR)
    variance_count = int(reconciliation["review_required"].sum()) if not reconciliation.empty else 0
    c = st.columns(4)
    c[0].metric("Estimates", len(estimates))
    c[1].metric("Invoices", len(invoices))
    c[2].metric("Invoice Variances", variance_count)
    c[3].metric("Review Items", len(build_review_queue(PHASE2_DIR)))
    st.subheader("Estimate vs Invoice")
    st.dataframe(reconciliation, use_container_width=True, hide_index=True)
    st.subheader("Vendor Estimates")
    show_table(estimates, "estimate_search", 300)
    st.subheader("Vendor Invoices")
    show_table(invoices, "invoice_search", 300)

with tabs[7]:
    st.header("Compliance & Campaigns")
    c = st.columns(3)
    c[0].metric("Inspections", len(compliance))
    c[1].metric("Campaigns / Recalls", len(campaigns))
    c[2].metric("Compliance Records", len(compliance))
    st.subheader("Campaigns / Recalls")
    show_table(campaigns, "campaign_search")
    st.subheader("Compliance Inspections")
    show_table(compliance, "compliance_search", 350)

with tabs[8]:
    st.header("Data Quality")
    st.caption("Technical data-foundation details are intentionally kept here rather than exposed as business-facing phase names.")
    p1_summary = []
    for name, df in p1.items():
        p1_summary.append({"area": name, "rows": len(df), "columns": len(df.columns), "missing_cells": int(df.isna().sum().sum())})
    p2_summary = []
    for name, df in p2.items():
        p2_summary.append({"area": name, "rows": len(df), "columns": len(df.columns), "missing_cells": int(df.isna().sum().sum())})
    st.subheader("Data Inventory")
    st.dataframe(pd.DataFrame(p1_summary + p2_summary), use_container_width=True, hide_index=True)
    st.subheader("Human Review Queue")
    show_table(build_review_queue(PHASE2_DIR), "review_search", 350)

st.divider()
st.caption("Read-only business dashboard. AI recommendations, automated approvals, and return-to-service decisions remain disabled until the appropriate governance and AI phases are implemented.")
