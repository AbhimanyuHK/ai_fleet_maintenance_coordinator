from __future__ import annotations

import pandas as pd
import streamlit as st

from app.repair_recommendations import RepairContext, recommend_repair
from app.phase3_retrieval import load_chunks


def _text(row: pd.Series, columns: list[str]) -> str:
    return " ".join(str(row[c]) for c in columns if c in row.index and pd.notna(row[c]))


def render_repair_recommendations(faults: pd.DataFrame, history: pd.DataFrame, estimates: pd.DataFrame, repair_notes: pd.DataFrame, knowledge_dir, equipment_col: str = "equipment_id") -> None:
    st.subheader("Repair Recommendations")
    st.caption("Review diagnostic evidence, vendor estimates, recurring repairs and warranty indicators. AI recommendations are advisory and require human approval.")
    frames = [x for x in [faults, history, estimates, repair_notes] if not x.empty and equipment_col in x.columns]
    if not frames:
        st.info("No equipment-linked repair data is available.")
        return
    equipment_ids = sorted(set(str(v) for frame in frames for v in frame[equipment_col].dropna().tolist()))
    equipment_id = st.selectbox("Equipment", equipment_ids, key="repair_equipment")
    f = faults[faults[equipment_col].astype(str).eq(equipment_id)] if equipment_col in faults.columns else pd.DataFrame()
    h = history[history[equipment_col].astype(str).eq(equipment_id)] if equipment_col in history.columns else pd.DataFrame()
    e = estimates[estimates[equipment_col].astype(str).eq(equipment_id)] if equipment_col in estimates.columns else pd.DataFrame()
    n = repair_notes[repair_notes[equipment_col].astype(str).eq(equipment_id)] if equipment_col in repair_notes.columns else pd.DataFrame()
    fault_codes = tuple(str(v) for col in ["fault_code", "code"] if col in f.columns for v in f[col].dropna().tolist())
    severities = tuple(str(v) for col in ["severity"] if col in f.columns for v in f[col].dropna().tolist())
    fault_description = _text(f, ["description", "fault_description", "message"])
    prior_repair_count = len(h)
    estimate_amount = None
    if not e.empty:
        for col in ["estimate_amount", "total_amount", "amount"]:
            if col in e.columns:
                numeric = pd.to_numeric(e[col], errors="coerce").dropna()
                if not numeric.empty:
                    estimate_amount = float(numeric.iloc[-1]); break
    prior_estimate_amount = None
    if len(e) > 1:
        for col in ["estimate_amount", "total_amount", "amount"]:
            if col in e.columns:
                numeric = pd.to_numeric(e[col], errors="coerce").dropna()
                if len(numeric) > 1:
                    prior_estimate_amount = float(numeric.iloc[-2]); break
    warranty_indicator = False
    warranty_text = _text(e, ["warranty_status", "warranty", "coverage"]).lower()
    warranty_indicator = any(x in warranty_text for x in ["potential", "pending", "denied", "warranty"])
    additional_text = _text(e, ["additional_work", "work_type", "description", "notes"]).lower()
    vendor_additional_work = any(x in additional_text for x in ["additional", "extra", "supplemental"])
    context = RepairContext(equipment_id, fault_codes, fault_description, prior_repair_count, estimate_amount, prior_estimate_amount, warranty_indicator, vendor_additional_work)
    if st.button("Generate Repair Recommendation", type="primary", key="generate_repair_recommendation"):
        result = recommend_repair(context, load_chunks(knowledge_dir))
        c = st.columns(5)
        c[0].metric("Priority", result.priority)
        c[1].metric("Estimate Variance", f"{result.estimate_variance:.1f}%" if result.estimate_variance is not None else "N/A")
        c[2].metric("Warranty Review", "YES" if result.warranty_review_required else "NO")
        c[3].metric("Evidence", len(result.evidence))
        c[4].metric("Approval", "REQUIRED")
        st.subheader("Recommendation")
        st.write(result.recommendation)
        st.subheader("Findings")
        for item in result.findings:
            st.write(f"• {item}")
        st.subheader("Evidence Sources")
        if result.evidence:
            for source in result.evidence:
                st.write(f"• {source}")
        else:
            st.warning("No approved evidence retrieved. Escalate for human review.")
        st.warning("No repair, payment, warranty decision or vendor approval is performed automatically.")
