from pathlib import Path
import pandas as pd
import streamlit as st
from app.phase2_data_quality import build_review_queue, reconcile_estimates_invoices
from app.phase3_retrieval import load_chunks, retrieve
from app.maintenance_recommendations import recommend
from app.communication_assistant import assess
from app.repair_recommendations_ui import render_repair_recommendations
from app.maintenance_scheduling_ui import render_maintenance_scheduling
from app.predictive_risk import RiskContext, assess_risk
from app.qwen_rag import MODEL_ID, ai_runtime_available, generate_answer

ROOT = Path(__file__).resolve().parent
P1 = ROOT / "data" / "phase1"; P2 = ROOT / "data" / "phase2"; KNOWLEDGE = ROOT / "data" / "phase3" / "knowledge"
P1_FILES = {"Equipment Master":"equipment_master.csv","PM Schedule":"pm_schedule.csv","Maintenance History":"maintenance_history.csv","Fault Events":"fault_events.csv","Work Orders":"work_orders.csv","Vendor Master":"vendor_master.csv","Service Locations":"service_locations.csv","Equipment Availability":"equipment_availability.csv","Campaigns / Recalls":"campaigns.csv","Compliance Inspections":"compliance_inspections.csv"}
P2_FILES = {"Communication Messages":"communication_messages.csv","Communication Participants":"communication_participants.csv","Voicemails":"voicemail_records.csv","Driver Requests":"driver_requests.csv","Vendor Estimates":"vendor_estimates.csv","Estimate Lines":"vendor_estimate_lines.csv","Vendor Invoices":"vendor_invoices.csv","Invoice Lines":"vendor_invoice_lines.csv","Repair Notes":"repair_notes.csv","Document Artifacts":"document_artifacts.csv","Human Review Tasks":"human_review_tasks.csv"}
st.set_page_config(page_title="Fleet Maintenance AI Coordinator", page_icon="🚛", layout="wide")
st.title("🚛 Fleet Maintenance AI Coordinator"); st.caption("Data foundation → grounded AI intelligence → human approval → operational action")
@st.cache_data
def load_csv(folder, filename): return pd.read_csv(folder / filename)
def load_group(folder, files): return {name: load_csv(folder, filename) for name,filename in files.items() if (folder/filename).exists()}
def show_table(df,key,height=400):
    if df.empty: st.info("No data available."); return
    q=st.text_input("Search",key=key); view=df
    if q.strip(): view=view[view.astype(str).apply(lambda c:c.str.contains(q,case=False,na=False)).any(axis=1)]
    st.dataframe(view,use_container_width=True,height=height,hide_index=True)
def count_value(df,col,value): return int(df[col].astype(str).str.upper().eq(value.upper()).sum()) if col in df else 0
def count_true(df,col): return int(df[col].astype(str).str.lower().eq("true").sum()) if col in df else 0
def dataframe_to_text(df):
    if df is None or df.empty: return ""
    values = df.astype(str).fillna("").to_numpy().ravel().tolist()
    return " ".join(v for v in values if v and v.lower() != "nan")
p1,p2=load_group(P1,P1_FILES),load_group(P2,P2_FILES)
fleet=p1.get("Equipment Master",pd.DataFrame()); pm=p1.get("PM Schedule",pd.DataFrame()); history=p1.get("Maintenance History",pd.DataFrame()); faults=p1.get("Fault Events",pd.DataFrame()); work_orders=p1.get("Work Orders",pd.DataFrame()); vendors=p1.get("Vendor Master",pd.DataFrame()); locations=p1.get("Service Locations",pd.DataFrame()); availability=p1.get("Equipment Availability",pd.DataFrame()); campaigns=p1.get("Campaigns / Recalls",pd.DataFrame()); compliance=p1.get("Compliance Inspections",pd.DataFrame()); requests=p2.get("Driver Requests",pd.DataFrame()); messages=p2.get("Communication Messages",pd.DataFrame()); voicemails=p2.get("Voicemails",pd.DataFrame()); estimates=p2.get("Vendor Estimates",pd.DataFrame()); invoices=p2.get("Vendor Invoices",pd.DataFrame()); repair_notes=p2.get("Repair Notes",pd.DataFrame())
review_queue=build_review_queue(P2); reconciliation=reconcile_estimates_invoices(P2)
section=st.sidebar.radio("Open",["📊 Data Foundation","🤖 AI Intelligence","👤 Human Approval"],label_visibility="collapsed"); st.sidebar.divider(); st.sidebar.caption("AI runtime"); st.sidebar.info(f"Model: {MODEL_ID}\n\nLocal runtime: {'Available' if ai_runtime_available() else 'Not installed'}\n\nHuman approval: Required")
if section=="📊 Data Foundation":
    st.header("📊 Data Foundation"); tabs=st.tabs(["Fleet Overview","PM Management","Faults & Alerts","Work Orders & Repairs","Driver Requests","Vendor Management","Estimates & Invoices","Compliance & Campaigns","Data Quality"])
    with tabs[0]:
        c=st.columns(6); c[0].metric("Equipment",len(fleet)); c[1].metric("PM Records",len(pm)); c[2].metric("Fault Events",len(faults)); c[3].metric("Open Work Orders",count_value(work_orders,"status","OPEN")); c[4].metric("Driver Requests",len(requests)); c[5].metric("Review Items",len(review_queue)); a,b=st.columns(2)
        with a:
            st.subheader("PM Status")
            if "status" in pm: st.bar_chart(pm["status"].value_counts())
        with b:
            st.subheader("Fault Severity")
            if "severity" in faults: st.bar_chart(faults["severity"].value_counts())
    with tabs[1]: st.subheader("PM Management"); c=st.columns(3); c[0].metric("Scheduled PM",len(pm)); c[1].metric("Due / Upcoming",sum(count_value(pm,"status",x) for x in ["DUE","UPCOMING","DUE_SOON"])); c[2].metric("Overdue",count_value(pm,"status","OVERDUE")); show_table(pm,"pm_search")
    with tabs[2]: st.subheader("Faults & Alerts"); c=st.columns(4); c[0].metric("Total Faults",len(faults)); c[1].metric("Critical",count_value(faults,"severity","CRITICAL")); c[2].metric("High",count_value(faults,"severity","HIGH")); c[3].metric("Safety Related",count_true(faults,"safety_related")); show_table(faults,"fault_search")
    with tabs[3]: st.subheader("Work Orders & Repairs"); c=st.columns(4); c[0].metric("Work Orders",len(work_orders)); c[1].metric("Open",count_value(work_orders,"status","OPEN")); c[2].metric("Repair Notes",len(repair_notes)); c[3].metric("Unavailable Fleet",len(availability)-count_value(availability,"status","AVAILABLE")); show_table(work_orders,"wo_search"); st.subheader("Repair Notes"); show_table(repair_notes,"repair_notes_search",300)
    with tabs[4]: st.subheader("Driver Requests"); c=st.columns(4); c[0].metric("Requests",len(requests)); c[1].metric("Safety Related",count_true(requests,"safety_related")); c[2].metric("Voicemails",len(voicemails)); c[3].metric("Messages",len(messages)); show_table(requests,"request_search"); st.subheader("Voicemails"); show_table(voicemails,"voicemail_search",300); st.subheader("Messages"); show_table(messages,"message_search",300)
    with tabs[5]: st.subheader("Vendor Management"); c=st.columns(3); c[0].metric("Vendors",len(vendors)); c[1].metric("Service Locations",len(locations)); c[2].metric("Vendor Estimates",len(estimates)); show_table(vendors,"vendor_search"); st.subheader("Service Locations"); show_table(locations,"location_search",300)
    with tabs[6]:
        variance_count=int(reconciliation["review_required"].sum()) if not reconciliation.empty and "review_required" in reconciliation else 0; st.subheader("Estimates & Invoices"); c=st.columns(4); c[0].metric("Estimates",len(estimates)); c[1].metric("Invoices",len(invoices)); c[2].metric("Invoice Variances",variance_count); c[3].metric("Review Items",len(review_queue)); st.dataframe(reconciliation,use_container_width=True,hide_index=True); st.subheader("Vendor Estimates"); show_table(estimates,"estimate_search",300); st.subheader("Vendor Invoices"); show_table(invoices,"invoice_search",300)
    with tabs[7]: st.subheader("Compliance & Campaigns"); c=st.columns(3); c[0].metric("Inspections",len(compliance)); c[1].metric("Campaigns / Recalls",len(campaigns)); c[2].metric("Compliance Records",len(compliance)); st.subheader("Campaigns / Recalls"); show_table(campaigns,"campaign_search"); st.subheader("Compliance Inspections"); show_table(compliance,"compliance_search",350)
    with tabs[8]: st.subheader("Data Quality"); rows=[{"Dataset":n,"Rows":len(df),"Columns":len(df.columns),"Missing Cells":int(df.isna().sum().sum())} for n,df in {**p1,**p2}.items()]; st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True); st.subheader("Human Review Queue"); show_table(review_queue,"review_search",350)
elif section=="🤖 AI Intelligence":
    st.header("🤖 AI Intelligence"); tabs=st.tabs(["Maintenance Knowledge Assistant","Maintenance Recommendations","Communication Assistant","Repair Recommendations","Maintenance Scheduling","Predictive Risk"])
    with tabs[0]:
        st.subheader("Maintenance Knowledge Assistant"); question=st.text_area("Ask a maintenance question",placeholder="What should be checked when a brake fault is reported?"); top_k=st.slider("Evidence documents",1,5,3)
        if st.button("Retrieve and Analyze",type="primary"):
            if not question.strip(): st.warning("Enter a question first.")
            else:
                results=retrieve(question,load_chunks(KNOWLEDGE),top_k=top_k)
                if not results: st.error("No approved knowledge evidence was retrieved.")
                else:
                    evidence=[]; st.success(f"Retrieved {len(results)} approved evidence items.")
                    for i,r in enumerate(results,1): chunk=r["chunk"]; label=f"[{i}] {chunk.document_id} — {chunk.title} — authority={chunk.authority} — score={r['score']}"; evidence.append(label+"\n"+chunk.text); st.markdown(f"**{label}**"); st.write(chunk.text)
                    if ai_runtime_available():
                        try: st.subheader("Grounded AI Answer"); st.write(generate_answer(question,evidence))
                        except Exception as exc: st.error(f"AI generation failed safely: {exc}")
                    else: st.info("Qwen runtime is not installed. Retrieval remains available.")
                    st.warning("Human approval is required before any operational action.")
    with tabs[1]:
        st.subheader("Maintenance Recommendations")
        if fleet.empty: st.info("No equipment data available.")
        else:
            eq_col="equipment_id" if "equipment_id" in fleet.columns else fleet.columns[0]; eq=st.selectbox("Equipment",fleet[eq_col].astype(str).tolist(),key="maintenance_equipment"); f=faults[faults[eq_col].astype(str).eq(eq)] if eq_col in faults.columns else faults; p=pm[pm[eq_col].astype(str).eq(eq)] if eq_col in pm.columns else pm; h=history[history[eq_col].astype(str).eq(eq)] if eq_col in history.columns else history; d=requests[requests[eq_col].astype(str).eq(eq)] if eq_col in requests.columns else requests
            if st.button("Generate Maintenance Recommendation",type="primary",key="maintenance_recommendation"):
                result=recommend(eq,dataframe_to_text(f),dataframe_to_text(d),dataframe_to_text(pd.concat([p,h],ignore_index=True)),load_chunks(KNOWLEDGE)); c=st.columns(4); c[0].metric("Priority",result.priority); c[1].metric("Evidence",len(result.evidence)); c[2].metric("Approval","Required"); c[3].metric("Equipment",result.equipment_id); st.subheader("Recommendation"); st.write(result.recommendation); st.subheader("Reasons"); [st.write(f"• {x}") for x in result.reasons]; st.subheader("Evidence Sources"); [st.write(f"• {x}") for x in result.evidence]; st.warning("No autonomous action is taken.")
    with tabs[2]:
        st.subheader("Communication Assistant"); st.caption("Classify driver communication and prepare a response draft. Nothing is sent automatically."); options=["Manual message"]+(["Driver request"] if not requests.empty else [])+(["Email/message"] if not messages.empty else [])+(["Voicemail"] if not voicemails.empty else []); source=st.selectbox("Input source",options); eq=None; text=""
        if source=="Manual message": eq=st.text_input("Equipment ID (optional)"); text=st.text_area("Driver message",height=140)
        else:
            df=requests if source=="Driver request" else messages if source=="Email/message" else voicemails; idcol="request_id" if "request_id" in df else "message_id" if "message_id" in df else "voicemail_id" if "voicemail_id" in df else df.columns[0]; selected=st.selectbox("Record",df[idcol].astype(str).tolist()); row=df[df[idcol].astype(str).eq(selected)].iloc[0]; eq=str(row.get("equipment_id")) if pd.notna(row.get("equipment_id")) else None; cols=[c for c in df.columns if any(k in c.lower() for k in ["message","text","body","transcript","description","request"])] ; text=" ".join(str(row[c]) for c in cols if pd.notna(row[c])); st.text_area("Source content",text,height=140,disabled=True)
        if st.button("Analyze Communication",type="primary",key="communication_analysis"):
            if not text.strip(): st.warning("Provide a communication first.")
            else:
                result=assess(text,load_chunks(KNOWLEDGE),eq); c=st.columns(5); c[0].metric("Category",result.category); c[1].metric("Priority",result.priority); c[2].metric("Safety","YES" if result.safety_related else "NO"); c[3].metric("Compliance","YES" if result.compliance_related else "NO"); c[4].metric("Approval","Required"); st.subheader("Summary"); st.write(result.summary); st.subheader("Draft Response"); st.text_area("Human-editable draft",result.draft_response,height=180); st.subheader("Evidence"); [st.write(f"• {x}") for x in result.evidence] if result.evidence else st.info("No approved evidence retrieved; escalate rather than invent guidance."); st.warning("Draft only — nothing is sent automatically.")
    with tabs[3]: render_repair_recommendations(faults,history,estimates,repair_notes,KNOWLEDGE)
    with tabs[4]: render_maintenance_scheduling(pm,availability,locations,KNOWLEDGE)
    with tabs[5]:
        st.subheader("Predictive Risk")
        st.caption("Explainable risk assessment from validated fleet signals. This is a decision-support foundation, not a trained failure-probability model.")
        if fleet.empty: st.info("No equipment data available.")
        else:
            eq_col="equipment_id" if "equipment_id" in fleet.columns else fleet.columns[0]
            equipment_ids=fleet[eq_col].astype(str).tolist(); equipment_id=st.selectbox("Equipment",equipment_ids,key="risk_equipment")
            def rows_for(df): return df[df[eq_col].astype(str).eq(equipment_id)] if eq_col in df.columns else pd.DataFrame()
            f=rows_for(faults); h=rows_for(history); w=rows_for(work_orders); a=rows_for(availability); p=rows_for(pm); r=rows_for(requests)
            def nmatch(df,col,values): return int(df[col].astype(str).str.upper().isin(values).sum()) if col in df else 0
            critical=nmatch(f,"severity",{"CRITICAL"}); high=nmatch(f,"severity",{"HIGH"}); safety=nmatch(f,"safety_related",{"TRUE","YES","1"}) + nmatch(r,"safety_related",{"TRUE","YES","1"}); open_wo=nmatch(w,"status",{"OPEN","IN_PROGRESS"}); recent_repairs=len(h); unavailable=bool(not a.empty and "status" in a.columns and str(a.iloc[-1]["status"]).upper() != "AVAILABLE"); overdue=nmatch(p,"status",{"OVERDUE"}) > 0
            c=st.columns(7); c[0].metric("Critical Faults",critical); c[1].metric("High Faults",high); c[2].metric("Safety Events",safety); c[3].metric("Open WOs",open_wo); c[4].metric("Recent Repairs",recent_repairs); c[5].metric("Overdue PM","YES" if overdue else "NO"); c[6].metric("Unavailable","YES" if unavailable else "NO")
            if st.button("Assess Predictive Risk",type="primary",key="predictive_risk_assess"):
                result=assess_risk(RiskContext(equipment_id,critical,high,safety,open_wo,overdue,recent_repairs,unavailable),load_chunks(KNOWLEDGE)); c=st.columns(4); c[0].metric("Risk Score",result.score); c[1].metric("Risk Level",result.level); c[2].metric("Evidence",len(result.evidence)); c[3].metric("Approval","Required"); st.subheader("Risk Factors"); [st.write(f"• {x}") for x in result.factors]; st.subheader("Recommended Action"); st.write(result.recommendation); st.subheader("Evidence Sources"); [st.write(f"• {x}") for x in result.evidence] if result.evidence else st.info("No approved evidence retrieved; escalate for human review."); st.warning("Risk assessment is advisory. It does not automatically ground equipment, stop service, authorize repair, or change a schedule.")
else:
    st.header("👤 Human Approval")
    if review_queue.empty: st.success("No review items currently require attention.")
    else: st.metric("Items Requiring Review",len(review_queue)); show_table(review_queue,"approval_search",500)
    st.info("Approval actions remain read-only until workflow authorization and audit controls are implemented.")
st.divider(); st.caption("Fleet Maintenance AI Coordinator • Grounded AI prototype • Recommendations require human approval.")
