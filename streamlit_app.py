from pathlib import Path

import pandas as pd
import streamlit as st


ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data" / "phase1"

DATASETS = {
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

st.set_page_config(page_title="Fleet Maintenance Data Control Tower", page_icon="🚛", layout="wide")

st.title("🚛 Fleet Maintenance Data Control Tower")
st.caption("Phase 1 — Data Foundation | Business Data Explorer")

if not DATA_DIR.exists():
    st.error(f"Phase 1 data directory not found: {DATA_DIR}")
    st.stop()

@st.cache_data
def load_data(filename: str) -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / filename)

available = {name: filename for name, filename in DATASETS.items() if (DATA_DIR / filename).exists()}
missing = [name for name, filename in DATASETS.items() if not (DATA_DIR / filename).exists()]

# KPI cards
frames = {name: load_data(filename) for name, filename in available.items()}
equipment = frames.get("Equipment Master", pd.DataFrame())
pm = frames.get("PM Schedule", pd.DataFrame())
faults = frames.get("Fault Events", pd.DataFrame())
work_orders = frames.get("Work Orders", pd.DataFrame())
vendors = frames.get("Vendor Master", pd.DataFrame())

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Datasets Available", len(available), f"of {len(DATASETS)}")
c2.metric("Equipment", len(equipment))
c3.metric("PM Records", len(pm))
c4.metric("Fault Events", len(faults))
c5.metric("Open Work Orders", int((work_orders["status"].str.upper() == "OPEN").sum()) if "status" in work_orders else 0)

if missing:
    st.warning("Missing datasets: " + ", ".join(missing))

st.divider()

st.subheader("Business Overview")
left, right = st.columns(2)
with left:
    if not pm.empty and "status" in pm:
        st.markdown("**PM status**")
        st.bar_chart(pm["status"].value_counts())
with right:
    if not faults.empty and "severity" in faults:
        st.markdown("**Fault severity**")
        st.bar_chart(faults["severity"].value_counts())

st.divider()

st.subheader("Explore Phase 1 Input Data")
selected = st.selectbox("Select dataset", list(available.keys()))
df = frames[selected]

f1, f2, f3 = st.columns(3)
with f1:
    st.metric("Rows", len(df))
with f2:
    st.metric("Columns", len(df.columns))
with f3:
    st.metric("Missing Cells", int(df.isna().sum().sum()))

search = st.text_input("Search across visible columns", placeholder="equipment ID, vendor, fault code, status...")
view = df.copy()
if search.strip():
    mask = view.astype(str).apply(lambda col: col.str.contains(search, case=False, na=False)).any(axis=1)
    view = view[mask]

st.dataframe(view, use_container_width=True, height=480, hide_index=True)

with st.expander("Data quality snapshot"):
    quality = pd.DataFrame({
        "column": df.columns,
        "dtype": [str(x) for x in df.dtypes],
        "non_null": [int(df[c].notna().sum()) for c in df.columns],
        "missing": [int(df[c].isna().sum()) for c in df.columns],
        "unique": [int(df[c].nunique(dropna=True)) for c in df.columns],
    })
    st.dataframe(quality, use_container_width=True, hide_index=True)

st.divider()
st.subheader("Operational Data Views")

view_name = st.radio(
    "Choose a business view",
    ["PM Due / Scheduling", "Critical & High Faults", "Aged Work Orders", "Vendors"],
    horizontal=True,
)

if view_name == "PM Due / Scheduling" and not pm.empty:
    st.dataframe(pm, use_container_width=True, hide_index=True)
elif view_name == "Critical & High Faults" and not faults.empty:
    high = faults[faults["severity"].str.upper().isin(["CRITICAL", "HIGH"])] if "severity" in faults else faults
    st.dataframe(high, use_container_width=True, hide_index=True)
elif view_name == "Aged Work Orders" and not work_orders.empty:
    wo = work_orders.copy()
    if "opened_at" in wo:
        wo["opened_at"] = pd.to_datetime(wo["opened_at"], errors="coerce", utc=True)
        wo["age_days"] = (pd.Timestamp.now(tz="UTC") - wo["opened_at"]).dt.days
        wo = wo[wo["age_days"] > 30].sort_values("age_days", ascending=False)
    st.dataframe(wo, use_container_width=True, hide_index=True)
elif view_name == "Vendors" and not vendors.empty:
    st.dataframe(vendors, use_container_width=True, hide_index=True)

st.caption("Phase 1 UI is read-only. AI recommendations and automated actions are intentionally out of scope until the data foundation is approved.")
