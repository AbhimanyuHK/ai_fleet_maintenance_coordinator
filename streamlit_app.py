from pathlib import Path
import pandas as pd
import streamlit as st
from app.phase2_data_quality import build_review_queue, reconcile_estimates_invoices
from app.phase3_retrieval import load_chunks, retrieve
from app.maintenance_recommendations import recommend
from app.communication_assistant import assess
from app.qwen_rag import MODEL_ID, ai_runtime_available, generate_answer

ROOT = Path(__file__).resolve().parent
PHASE1_DIR = ROOT / "data" / "phase1"
PHASE2_DIR = ROOT / "data" / "phase2"
KNOWLEDGE_DIR = ROOT / "data" / "phase3" / "knowledge"
PHASE1_DATASETS = {"Equipment Master":"equipment_master.csv","PM Schedule":"pm_schedule.csv","Maintenance History":"maintenance_history.csv","Fault Events":"fault_events.csv","Work Orders":"work_orders.csv","Vendor Master":"vendor_master.csv","Service Locations":"service_locations.csv","Equipment Availability":"equipment_availability.csv","Campaigns / Recalls":"campaigns.csv","Compliance Inspections":"compliance_inspections.csv"}
PHASE2_DATASETS = {"Communication Messages":"communication_messages.csv","Communication Participants":"communication_participants.csv","Voicemails":"voicemail_records.csv","Driver Requests":"driver_requests.csv","Vendor Estimates":"vendor_estimates.csv","Estimate Lines":"vendor_estimate_lines.csv","Vendor Invoices":"vendor_invoices.csv","Invoice Lines":"vendor_invoice_lines.csv","Repair Notes":"repair_notes.csv","Document Artifacts":"document_artifacts.csv","Human Review Tasks":"human_review_tasks.csv"}

st.set_page_config(page_title="Fleet Maintenance AI Coordinator", page_icon="🚛", layout="wide")
st.title("🚛 Fleet Maintenance AI Coordinator")
st.caption("Data foundation → grounded AI intelligence → human approval → operational action")

@st.cache_data
def load_csv(directory, filename): return pd.read_csv(directory / filename)
def load_group(directory, datasets): return {n: load_csv(directory, f) for n, f in datasets.items() if (directory / f).exists()}
def safe_bool_count(df, col, value="true"): return int(df[col].astype(str).str.lower().eq(value).sum()) if col in df else 0
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
st.sidebar.divider(); st.sidebar.caption("AI runtime")
st.sidebar.info(f"Model: {MODEL_ID}\n\nLocal runtime: {'Available' if ai_runtime_available() else 'Not installed'}\n\nHuman approval: Required")

if section == "📊 Data Foundation":
    st.header("📊 Data Foundation")
    tabs=st.tabs(["Fleet Overview","PM Management","Faults & Alerts","Work Orders & Repairs","Driver Requests","Vendor Management","Estimates & Invoices","Compliance & Campaigns","Data Quality"])
    with tabs[0]:
        st.subheader("Fleet Overview"); c=st.columns(6); c[0].metric("Equipment",len(fleet)); c[1].metric("PM Records",len(pm)); c[2].metric("Fault Events",len(faults)); c[3].metric("Open Work Orders",int(work_orders.get("status",pd.Series(dtype=str)).astype(str).str.upper().eq("OPEN").sum())); c[4].metric("Driver Requests",len(requests)); c[5].metric("Review Items",len(review_queue)); a,b=st.columns(2)
        with a:
            st.subheader("PM Status")
            if not pm.empty and "status" in pm: st.bar_chart(pm["status"].value_counts())
        with b:
            st.subheader("Fault Severity")
            if not faults.empty and "severity" in faults: st.bar_chart(faults["severity"].value_counts())
    with tabs[1]:
        st.subheader("PM Management"); c=st.columns(3); c[0].metric("Scheduled PM",len(pm)); c[1].metric("Due / Upcoming",int(pm.get("status",pd.Series(dtype=str)).astype(str).str.upper().isin(["DUE","UPCOMING","DUE_SOON"]).sum())); c[2].metric("Overdue",int(pm.get("status",pd.Series(dtype=str)).astype(str).str.upper().eq("OVERDUE").sum())); show_table(pm,"pm_search")
    with tabs[2]:
        st.subheader("Faults & Alerts"); c=st.columns(4); c[0].metric("Total Faults",len(faults)); c[1].metric("Critical",int(faults.get("severity",pd.Series(dtype=str)).astype(str).str.upper().eq("CRITICAL").sum())); c[2].metric("High",int(faults.get("severity",pd.Series(dtype=str)).astype(str).str.upper().eq("HIGH").sum())); c[3].metric("Safety Related",safe_bool_count(faults,"safety_related")); show_table(faults,"fault_search")
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
        st.subheader("Data Quality"); rows=[]
        for name,df in {**p1,**p2}.items(): rows.append({"Dataset":name,"Rows":len(df),"Columns":len(df.columns),"Missing Cells":int(df.isna().sum().sum())})
        st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True); st.subheader("Human Review Queue"); show_table(review_queue,"review_search",350)

elif section == "🤖 AI Intelligence":
    st.header("🤖 AI Intelligence")
    ai_tabs=st.tabs(["Maintenance Knowledge Assistant","Maintenance Recommendations","Communication Assistant","Repair Recommendations","Maintenance Scheduling","Predictive Risk"])
    with ai_tabs[0]:
        st.subheader("Maintenance Knowledge Assistant")
        question=st.text_area("Ask a maintenance question",placeholder="Example: What should be checked when a brake fault is reported?",height=100)
        top_k=st.slider("Evidence documents",1,5,3)
        if st.button("Retrieve and Analyze",type="primary"):
            if not question.strip(): st.warning("Enter a maintenance question first.")
            else:
                chunks=load_chunks(KNOWLEDGE_DIR); results=retrieve(question,chunks,top_k=top_k)
                if not results: st.error("No approved knowledge evidence was retrieved. No recommendation should be made.")
                else:
                    st.success(f"Retrieved {len(results)} approved evidence items.")
                    evidence=[]
                    for i,r in enumerate(results,1):
                        c=r["chunk"]; label=f"[{i}] {c.document_id} — {c.title} — authority={c.authority} — score={r['score']}"; evidence.append(label+"\n"+c.text); st.markdown(f"**{label}**"); st.write(c.text)
                    if ai_runtime_available():
                        try: st.subheader("Grounded AI Answer"); st.write(generate_answer(question,evidence))
                        except Exception as exc: st.error(f"AI generation failed safely: {exc}")
                    else: st.info("Qwen runtime is not installed. Retrieval is working; install requirements-ai.txt to enable local generation.")
                    st.warning("Human approval is required before any maintenance, repair, financial or return-to-service action.")
    with ai_tabs[1]:
        st.subheader("Maintenance Recommendations")
        st.caption("Combines operational maintenance context with approved knowledge evidence. Recommendations are advisory only.")
        if fleet.empty: st.info("No equipment data is available.")
        else:
            equipment_col = "equipment_id" if "equipment_id" in fleet.columns else fleet.columns[0]
            equipment_id = st.selectbox("Equipment", fleet[equipment_col].astype(str).tolist())
            eq_faults = faults[faults[equipment_col].astype(str).eq(str(equipment_id))] if equipment_col in faults.columns else faults
            eq_pm = pm[pm[equipment_col].astype(str).eq(str(equipment_id))] if equipment_col in pm.columns else pm
            eq_history = p1.get("Maintenance History", pd.DataFrame()); eq_history = eq_history[eq_history[equipment_col].astype(str).eq(str(equipment_id))] if equipment_col in eq_history.columns else eq_history
            fault_text = " ".join(eq_faults.astype(str).fillna("").agg(" ".join, axis=1).tolist()); maintenance_context = " ".join(eq_pm.astype(str).fillna("").agg(" ".join, axis=1).tolist() + eq_history.astype(str).fillna("").agg(" ".join, axis=1).tolist()); driver_text = " ".join(requests[requests[equipment_col].astype(str).eq(str(equipment_id))].astype(str).fillna("").agg(" ".join, axis=1).tolist()) if equipment_col in requests.columns else ""
            if st.button("Generate Maintenance Recommendation",type="primary"):
                result = recommend(str(equipment_id), fault_text, driver_text, maintenance_context, load_chunks(KNOWLEDGE_DIR)); c=st.columns(4); c[0].metric("Priority",result.priority); c[1].metric("Evidence",len(result.evidence)); c[2].metric("Approval","Required"); c[3].metric("Equipment",result.equipment_id); st.subheader("Recommendation"); st.write(result.recommendation); st.subheader("Reasons"); [st.write(f"• {r}") for r in result.reasons]; st.subheader("Evidence Sources"); [st.write(f"• {source}") for source in result.evidence]; st.warning("No autonomous action is taken. Human approval is required.")
    with ai_tabs[2]:
        st.subheader("Communication Assistant")
        st.caption("Classify driver communication, prioritize safety/compliance, retrieve evidence and prepare a response draft. Nothing is sent automatically.")
        source_options=["Manual message"]
        if not requests.empty: source_options.append("Driver request")
        if not messages.empty: source_options.append("Email/message")
        if not voicemails.empty: source_options.append("Voicemail")
        source=st.selectbox("Input source",source_options)
        equipment_id=None; message_text=""
        if source == "Manual message":
            equipment_id=st.text_input("Equipment ID (optional)"); message_text=st.text_area("Driver message",height=140,placeholder="Paste the driver email, voicemail transcription, or request...")
        else:
            source_df=requests if source=="Driver request" else messages if source=="Email/message" else voicemails
            display_col="request_id" if "request_id" in source_df else "message_id" if "message_id" in source_df else "voicemail_id" if "voicemail_id" in source_df else source_df.columns[0]
            selected=st.selectbox("Record",source_df[display_col].astype(str).tolist())
            row=source_df[source_df[display_col].astype(str).eq(str(selected))].iloc[0]
            equipment_id=str(row.get("equipment_id")) if pd.notna(row.get("equipment_id")) else None
            text_cols=[c for c in source_df.columns if any(x in c.lower() for x in ["message","text","body","transcript","description","request"])]
            message_text=" ".join(str(row[c]) for c in text_cols if pd.notna(row[c]))
            st.text_area("Source content",message_text,height=140,disabled=True)
        if st.button("Analyze Communication",type="primary"):
            if not message_text.strip(): st.warning("Provide or select a driver communication first.")
            else:
                result=assess(message_text,load_chunks(KNOWLEDGE_DIR),equipment_id)
                c=st.columns(5); c[0].metric("Category",result.category); c[1].metric("Priority",result.priority); c[2].metric("Safety","YES" if result.safety_related else "NO"); c[3].metric("Compliance","YES" if result.compliance_related else "NO"); c[4].metric("Approval","Required")
                st.subheader("Summary"); st.write(result.summary)
                st.subheader("Draft Response"); st.text_area("Human-editable draft",result.draft_response,height=180)
                st.subheader("Evidence");
                if result.evidence:
                    for source_id in result.evidence: st.write(f"• {source_id}")
                else: st.info("No approved knowledge evidence was retrieved. Escalate rather than invent guidance.")
                st.warning("Draft only — no email, voicemail response, repair, or financial action is sent automatically.")
    descriptions=[("Repair Recommendations","Combine fault codes, maintenance history, repair notes, OEM knowledge and vendor information to suggest diagnostic and repair options."),("Maintenance Scheduling","Combine due dates, equipment availability, vendor preferences, service capacity and operational constraints to recommend a low-disruption schedule."),("Predictive Risk","Estimate equipment failure risk from maintenance history, fault patterns, telemetry and operational signals, with explainable risk factors.")]
    for tab,(title,desc) in zip(ai_tabs[3:],descriptions):
        with tab: st.subheader(title); st.write(desc); a,b,c=st.columns(3); a.metric("Status","Foundation Ready"); b.metric("Model","Qwen 2.5 3B"); c.metric("Human Approval","Required"); st.info("This capability will consume validated operational data + RAG evidence. No autonomous operational decision is enabled.")
else:
    st.header("👤 Human Approval"); st.caption("Safety, compliance, financial and operational decisions remain under human control.")
    if review_queue.empty: st.success("No review items currently require attention.")
    else: st.metric("Items Requiring Review",len(review_queue)); show_table(review_queue,"approval_search",500); st.info("Approval actions are intentionally read-only until workflow authorization and audit controls are implemented.")

st.divider(); st.caption("Fleet Maintenance AI Coordinator • Grounded AI prototype • Recommendations require human approval.")
