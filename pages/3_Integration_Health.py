import pandas as pd
import streamlit as st

from app.integration_health import build_health_report
from app.integration_pipeline import IntegrationStore
from app.integrations import IntegrationSource, build_demo_adapters

st.set_page_config(page_title="Integration Health | Fleet Maintenance AI", page_icon="🔌", layout="wide")
st.title("🔌 Integration Health")
st.caption("Business-facing monitoring for TMT, OEM, ELD, PFJ, and vendor data feeds. Demo adapters are synthetic and do not call external systems.")

if st.button("Refresh Synthetic Integration Data", type="primary"):
    store = IntegrationStore()
    for _, adapter in build_demo_adapters().items():
        store.ingest(adapter, adapter.fetch().records)
    st.session_state["integration_health_store"] = store

store = st.session_state.get("integration_health_store")
if store is None:
    st.info("Select **Refresh Synthetic Integration Data** to load the safe demo integration signals.")
    st.stop()

report = build_health_report(store)
rows = [
    {
        "Source": item.source,
        "Freshness": item.freshness,
        "Accepted": item.accepted,
        "Rejected": item.rejected,
        "Duplicates": item.duplicates,
        "Last Ingestion": item.last_ingestion.isoformat() if item.last_ingestion else "—",
    }
    for item in report
]
health_df = pd.DataFrame(rows)

st.subheader("Source Health")
metric_columns = st.columns(5)
for index, source in enumerate([
    IntegrationSource.TMT.value,
    IntegrationSource.OEM.value,
    IntegrationSource.ELD.value,
    IntegrationSource.PFJ.value,
    IntegrationSource.VENDOR.value,
]):
    item = next(item for item in report if item.source == source)
    metric_columns[index].metric(source, item.freshness)

st.dataframe(health_df, use_container_width=True, hide_index=True)

attention = health_df[health_df["Freshness"].isin(["STALE", "OUTDATED", "NO_DATA"])]
if attention.empty:
    st.success("All configured demo integrations are fresh.")
else:
    st.warning(f"{len(attention)} integration source(s) require attention.")
    st.dataframe(attention, use_container_width=True, hide_index=True)

st.subheader("Audit Activity")
audit_df = pd.DataFrame([
    {
        "Source": event.source,
        "Action": event.action,
        "External ID": event.external_id,
        "Accepted": event.accepted,
        "Detail": event.detail,
        "Occurred": event.occurred_at.isoformat(),
    }
    for event in store.audit
])
st.dataframe(audit_df, use_container_width=True, hide_index=True)

st.info("Monitoring only: this page does not authorize repairs, change schedules, or send updates to external systems.")
st.caption("Phase 4 integration foundation • Synthetic data only • Human approval required")
