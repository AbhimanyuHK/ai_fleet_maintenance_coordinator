from __future__ import annotations
from datetime import date
import pandas as pd
import streamlit as st
from app.maintenance_scheduling import SchedulingContext, recommend_schedule
from app.phase3_retrieval import load_chunks


def render_maintenance_scheduling(pm: pd.DataFrame, availability: pd.DataFrame, locations: pd.DataFrame, knowledge_dir):
    st.subheader("Maintenance Scheduling")
    st.caption("Recommend low-disruption PM windows while enforcing the five-day planning rule. Scheduling remains human-approved.")
    if pm.empty:
        st.info("No PM schedule data is available.")
        return
    equipment_col = "equipment_id" if "equipment_id" in pm.columns else pm.columns[0]
    due_col = next((c for c in pm.columns if c.lower() in {"due_date", "pm_due_date", "scheduled_due_date"}), None)
    if not due_col:
        st.warning("PM dataset does not contain a recognized due-date column.")
        return
    options = pm[equipment_col].astype(str).unique().tolist()
    equipment_id = st.selectbox("Equipment", options)
    row = pm[pm[equipment_col].astype(str).eq(equipment_id)].iloc[0]
    due_date = pd.to_datetime(row[due_col]).date()
    proposed = st.date_input("Proposed service date", value=max(date.today(), due_date - pd.Timedelta(days=5)))
    available = True
    if not availability.empty and equipment_col in availability.columns and "status" in availability.columns:
        a = availability[availability[equipment_col].astype(str).eq(equipment_id)]
        if not a.empty: available = str(a.iloc[-1]["status"]).upper() == "AVAILABLE"
    preferred = st.checkbox("Preferred vendor/service location selected", value=True)
    conflict = st.checkbox("Operational conflict exists", value=False)
    if st.button("Evaluate Schedule", type="primary"):
        result = recommend_schedule(SchedulingContext(equipment_id, due_date, proposed, available, preferred, conflict), load_chunks(knowledge_dir))
        c = st.columns(4)
        c[0].metric("Priority", result.priority)
        c[1].metric("PM Due", due_date.isoformat())
        c[2].metric("Recommended", result.recommended_date.isoformat() if result.recommended_date else "Coordinate")
        c[3].metric("Approval", "Required")
        st.subheader("Recommendation")
        st.write(result.recommendation)
        st.subheader("Reasons")
        for reason in result.reasons: st.write(f"• {reason}")
        st.subheader("Evidence")
        for source in result.evidence: st.write(f"• {source}")
        st.warning("No appointment or equipment schedule is changed automatically. Human approval is required.")
