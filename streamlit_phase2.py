from pathlib import Path
import pandas as pd
import streamlit as st
from app.phase2_data_quality import reconcile_estimates_invoices, build_review_queue

ROOT=Path(__file__).resolve().parent
DATA=ROOT/"data"/"phase2"
FILES={
"Communications":"communication_messages.csv","Participants":"communication_participants.csv","Voicemails":"voicemail_records.csv","Driver Requests":"driver_requests.csv","Vendor Estimates":"vendor_estimates.csv","Estimate Lines":"vendor_estimate_lines.csv","Vendor Invoices":"vendor_invoices.csv","Invoice Lines":"vendor_invoice_lines.csv","Repair Notes":"repair_notes.csv","Documents":"document_artifacts.csv","Human Review Tasks":"human_review_tasks.csv"}

st.set_page_config(page_title="Fleet Maintenance — Phase 2",page_icon="📨",layout="wide")
st.title("📨 Fleet Maintenance — Phase 2 Data Control Tower")
st.caption("AI Intake Foundation | Read-only business data explorer")

@st.cache_data
def load(name): return pd.read_csv(DATA/FILES[name])
frames={n:load(n) for n in FILES if (DATA/FILES[n]).exists()}
req=frames.get("Driver Requests",pd.DataFrame()); est=frames.get("Vendor Estimates",pd.DataFrame()); inv=frames.get("Vendor Invoices",pd.DataFrame()); vm=frames.get("Voicemails",pd.DataFrame())
q=build_review_queue(DATA); rec=reconcile_estimates_invoices(DATA)

c1,c2,c3,c4,c5=st.columns(5)
c1.metric("Datasets",len(frames),f"of {len(FILES)}")
c2.metric("Driver Requests",len(req))
c3.metric("Voicemails",len(vm))
c4.metric("Vendor Estimates",len(est))
c5.metric("Review Items",len(q))

st.divider(); st.subheader("Business Risk Snapshot")
a,b=st.columns(2)
with a:
 st.markdown("**Human review queue**"); st.dataframe(q,use_container_width=True,hide_index=True)
with b:
 st.markdown("**Estimate → invoice reconciliation**"); st.dataframe(rec,use_container_width=True,hide_index=True)

st.divider(); st.subheader("Explore Phase 2 Input Data")
selected=st.selectbox("Dataset",list(frames)); df=frames[selected]
search=st.text_input("Search",placeholder="request, work order, vendor, subject...")
view=df
if search.strip():
 mask=view.astype(str).apply(lambda c:c.str.contains(search,case=False,na=False)).any(axis=1); view=view[mask]
st.dataframe(view,use_container_width=True,height=500,hide_index=True)

st.divider(); st.subheader("Phase 2 Controls")
st.info("AI is intentionally disabled. This screen exposes validated business inputs, financial variance signals, document lineage, and human-review cases before AI is introduced.")
