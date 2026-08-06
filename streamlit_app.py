from pathlib import Path
import pandas as pd
import streamlit as st
from app.phase2_data_quality import build_review_queue, reconcile_estimates_invoices

ROOT = Path(__file__).resolve().parent
PHASE1_DIR = ROOT / "data" / "phase1"
PHASE2_DIR = ROOT / "data" / "phase2"

PHASE1_DATASETS = {"Equipment Master":"equipment_master.csv","PM Schedule":"pm_schedule.csv","Maintenance History":"maintenance_history.csv","Fault Events":"fault_events.csv","Work Orders":"work_orders.csv","Vendor Master":"vendor_master.csv","Service Locations":"service_locations.csv","Equipment Availability":"equipment_availability.csv","Campaigns / Recalls":"campaigns.csv","Compliance Inspections":"compliance_inspections.csv"}
PHASE2_DATASETS = {"Communication Messages":"communication_messages.csv","Communication Participants":"communication_participants.csv","Voicemails":"voicemail_records.csv","Driver Requests":"driver_requests.csv","Vendor Estimates":"vendor_estimates.csv","Estimate Lines":"vendor_estimate_lines.csv","Vendor Invoices":"vendor_invoices.csv","Invoice Lines":"vendor_invoice_lines.csv","Repair Notes":"repair_notes.csv","Document Artifacts":"document_artifacts.csv","Human Review Tasks":"human_review_tasks.csv"}

st.set_page_config(page_title="Fleet Maintenance AI Coordinator", page_icon="🚛", layout="wide")
st.title("🚛 Fleet Maintenance AI Coordinator")
st.caption("Data foundation → AI intelligence → human approval → operational action")

@st.cache_data
def load_csv(directory, filename): return pd.read_csv(directory / filename)

def load_group(directory, datasets): return {n: load_csv(directory, f) for n, f in datasets.items() if (directory / f).exists()}

def safe_bool_count(df, col, value="true"):
    return int(df[col].astype(str).str.lower().eq(value).sum()) if col in df else 0

def show_table(df, key, height=420):
    if df.empty: st.info("No data available for this view."); return
    query = st.text_input("Search", key=key, placeholder="Search records...")
    view = df.copy()
    if query.strip():
        mask = view.astype(str).apply(lambda c: c.str.contains(query, case=False, na=False)).any(axis=1); view = view[mask]
    st.dataframe(view, use_container_width=True, height=height, hide_index=True)

p1, p2 = load_group(PHASE1_DIR, PHASE1_DATASETS), load_group(PHASE2_DIR, PHASE2_DATASETS)
fleet=p1.get("Equipment Master",pd.DataFrame()); pm=p1.get("PM Schedule",pd.DataFrame()); faults=p1.get("Fault Events",pd.DataFrame()); work_orders=p1.get("Work Orders",pd.DataFrame()); vendors=p1.get("Vendor Master",pd.DataFrame()); availability=p1.get("Equipment Availability",pd.DataFrame()); campaigns=p1.get("Campaigns / Recalls",pd.DataFrame()); compliance=p1.get("Compliance Inspections",pd.DataFrame()); requests=p2.get("Driver Requests",pd.DataFrame()); messages=p2.get("Communication Messages",pd.DataFrame()); voicemails=p2.get("Voicemails",pd.DataFrame()); estimates=p2.get("Vendor Estimates",pd.DataFrame()); invoices=p2.get("Vendor Invoices",pd.DataFrame()); repair_notes=p2.get("Repair Notes",pd.DataFrame())
review_queue=build_review_queue(PHASE2_DIR); reconciliation=reconcile_estimates_invoices(PHASE2_DIR)

st.sidebar.header("Navigation")
section = st.sidebar.radio("Open", ["📊 Data Foundation", "🤖 AI Intelligence", "👤 Human Approval"], label_visibility="collapsed")
st.sidebar.divider(); st.sidebar.caption("Current AI status")
st.sidebar.info("AI engine: Not connected\n\nRAG: Not configured\n\nPrediction model: Not configured")

if section == "📊 Data Foundation":
    st.header("📊 Data Foundation")
    st.caption("Trusted operational inputs, cleaning, validation, standardization and data quality.")
    tabs=st.tabs(["Fleet Overview","PM Management","Faults & Alerts","Work Orders & Repairs","Driver Requests","Vendor Management","Estimates & Invoices","Compliance & Campaigns","Data Quality"])
    with tabs[0]:
        st.subheader("Fleet Overview"); c=st.columns(6); c[0].metric("Equipment",len(fleet)); c[1].metric("PM Records",len(pm)); c[2].metric("Fault Events",len(faults)); c[3].metric("Open Work Orders",int(work_orders.get("status",pd.Series(dtype=str)).astype(str).str.upper().eq("OPEN").sum())); c[4].metric("Driver Requests",len(requests)); c[5].metric("Review Items",len(review_queue))
        a,b=st.columns(2)
        with a:
            st.subheader("PM Status")
            if not pm.empty and "status" in pm: st.bar_chart(pm["status"].value_counts())
        with b:
            st.subheader("Fault Severity")
            if not faults.empty and "severity" in faults: st.bar_chart(faults["severity"].value_counts())
    with tabs[1]:
        st.subheader("PM Management")
        if not pm.empty:
            c=st.columns(3); c[0].metric("Scheduled PM",len(pm)); c[1].metric("Due / Upcoming",int(pm.get("status",pd.Series(dtype=str)).astype(str).str.upper().isin(["DUE","UPCOMING","DUE_SOON"]).sum())); c[2].metric("Overdue",int(pm.get("status",pd.Series(dtype=str)).astype(str).str.upper().eq("OVERDUE").sum()))
        show_table(pm,"pm_search")
    with tabs[2]:
        st.subheader("Faults & Alerts")
        c=st.columns(4); c[0].metric("Total Faults",len(faults)); c[1].metric("Critical",int(faults.get("severity",pd.Series(dtype=str)).astype(str).str.upper().eq("CRITICAL").sum())); c[2].metric("High",int(faults.get("severity",pd.Series(dtype=str)).astype(str).str.upper().eq("HIGH").sum())); c[3].metric("Safety Related",safe_bool_count(faults,"safety_related")); show_table(faults,"fault_search")
    with tabs[3]:
        st.subheader("Work Orders & Repairs"); c=st.columns(4); c[0].metric("Work Orders",len(work_orders)); c[1].metric("Open",int(work_orders.get("status",pd.Series(dtype=str)).astype(str).str.upper().eq("OPEN").sum())); c[2].metric("Repair Notes",len(repair_notes)); c[3].metric("Unavailable Fleet",int(availability.get("status",pd.Series(dtype=str)).astype(str).str.upper().ne("AVAILABLE").sum())); show_table(work_orders,"work_order_search"); st.subheader("Repair Notes"); show_table(repair_notes,"repair_note_search",300)
    with tabs[4]:
        st.subheader("Driver Requests"); c=st.columns(4); c[0].metric("Requests",len(requests)); c[1].metric("Safety Related",safe_bool_count(requests,"safety_related")); c[2].metric("Voicemails",len(voicemails)); c[3].metric("Messages",len(messages)); show_table(requests,"driver_request_search"); st.subheader("Voicemails"); show_table(voicemails,"voicemail_search",300); st.subheader("Communication Messages"); show_table(messages,"message_search",300)
    with tabs[5]:
        locations=p1.get("Service Locations",pd.DataFrame()); st.subheader("Vendor Management"); c=st.columns(3); c[0].metric("Vendors",len(vendors)); c[1].metric("Service Locations",len(locations)); c[2].metric("Vendor Estimates",len(estimates)); show_table(vendors,"vendor_search"); st.subheader("Preferred / Service Locations"); show_table(locations,"location_search",300)
    with tabs[6]:
        variance_count=int(reconciliation["review_required"].sum()) if not reconciliation.empty else 0; st.subheader("Estimates & Invoices"); c=st.columns(4); c[0].metric("Estimates",len(estimates)); c[1].metric("Invoices",len(invoices)); c[2].metric("Invoice Variances",variance_count); c[3].metric("Review Items",len(review_queue)); st.dataframe(reconciliation,use_container_width=True,hide_index=True); st.subheader("Vendor Estimates"); show_table(estimates,"estimate_search",300); st.subheader("Vendor Invoices"); show_table(invoices,"invoice_search",300)
    with tabs[7]:
        st.subheader("Compliance & Campaigns"); c=st.columns(3); c[0].metric("Inspections",len(compliance)); c[1].metric("Campaigns / Recalls",len(campaigns)); c[2].metric("Compliance Records",len(compliance)); st.subheader("Campaigns / Recalls"); show_table(campaigns,"campaign_search"); st.subheader("Compliance Inspections"); show_table(compliance,"compliance_search",350)
    with tabs[8]:
        st.subheader("Data Quality"); st.caption("Operational data health across all current input datasets."); rows=[]
        for name,df in {**p1,**p2}.items(): rows.append({"Dataset":name,"Rows":len(df),"Columns":len(df.columns),"Missing Cells":int(df.isna().sum().sum())})
        st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True); st.subheader("Human Review Queue"); show_table(review_queue,"review_search",350)

elif section == "🤖 AI Intelligence":
    st.header("🤖 AI Intelligence")
    st.caption("AI capabilities are designed here first; model execution is intentionally disabled until the knowledge and governance foundations are ready.")
    st.warning("AI Engine is not connected yet. The cards below are the production capability targets, not simulated AI decisions.")
    ai_tabs=st.tabs(["Maintenance Recommendations","Communication Assistant","Repair Recommendations","Maintenance Scheduling","Predictive Risk"])
    cards=[
        ("Maintenance Recommendations","Use PM history, faults, equipment condition, maintenance history and OEM guidance to recommend the next maintenance action."),
        ("Communication Assistant","Classify driver emails and voicemail, identify safety/compliance priority, summarize the request and draft a response for human approval."),
        ("Repair Recommendations","Combine fault codes, maintenance history, repair notes, OEM knowledge and vendor information to suggest diagnostic and repair options."),
        ("Maintenance Scheduling","Combine due dates, equipment availability, vendor preferences, service capacity and operational constraints to recommend a low-disruption schedule."),
        ("Predictive Risk","Estimate equipment failure risk from maintenance history, fault patterns, telemetry and operational signals, with explainable risk factors."),
    ]
    for tab,(title,desc) in zip(ai_tabs,cards):
        with tab:
            st.subheader(title); st.write(desc); a,b,c=st.columns(3); a.metric("Status","Not Connected"); b.metric("Model","Not Configured"); c.metric("Human Approval","Required")
            st.info("No AI recommendation is generated from this screen yet. This prevents synthetic/demo data from being presented as a real operational decision.")
            st.markdown("**Planned flow**"); st.code("Trusted Data → AI/ML → Recommendation → Confidence & Evidence → Human Approval → Action",language="text")

else:
    st.header("👤 Human Approval")
    st.caption("Safety, compliance, financial and operational decisions remain under human control.")
    if review_queue.empty: st.success("No review items currently require attention.")
    else:
        st.metric("Items Requiring Review",len(review_queue)); show_table(review_queue,"approval_search",500)
        st.info("Approval actions are intentionally read-only until workflow authorization and audit controls are implemented.")

st.divider()
st.caption("Fleet Maintenance AI Coordinator • Read-only demonstration • AI recommendations, automated approvals and return-to-service decisions are disabled until governed AI workflows are implemented.")
