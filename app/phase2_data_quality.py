from __future__ import annotations

from pathlib import Path
from typing import Any
import pandas as pd

DATASETS = {
    "communication_messages":"communication_messages.csv","communication_participants":"communication_participants.csv","voicemail_records":"voicemail_records.csv","driver_requests":"driver_requests.csv","vendor_estimates":"vendor_estimates.csv","vendor_estimate_lines":"vendor_estimate_lines.csv","vendor_invoices":"vendor_invoices.csv","vendor_invoice_lines":"vendor_invoice_lines.csv","repair_notes":"repair_notes.csv","document_artifacts":"document_artifacts.csv","human_review_tasks":"human_review_tasks.csv",
}
KEYS = {k:k.replace("communication_messages","message_id").replace("communication_participants","participant_id").replace("voicemail_records","voicemail_id").replace("driver_requests","request_id").replace("vendor_estimates","estimate_id").replace("vendor_estimate_lines","estimate_line_id").replace("vendor_invoices","invoice_id").replace("vendor_invoice_lines","invoice_line_id").replace("repair_notes","repair_note_id").replace("document_artifacts","document_artifact_id").replace("human_review_tasks","review_task_id") for k in DATASETS}
REQUIRED = {
"communication_messages":["message_id","channel","direction","sender_type","received_at","source_system","source_record_id","ingested_at"],
"communication_participants":["participant_id","message_id","participant_type","contact_reference"],
"voicemail_records":["voicemail_id","received_at","duration_seconds","caller_type","transcription_status","safety_related","source_system","source_record_id","ingested_at"],
"driver_requests":["request_id","request_type","priority","safety_related","status","created_at","source_system","source_record_id","ingested_at"],
"vendor_estimates":["estimate_id","work_order_id","vendor_id","estimate_number","estimate_date","total_estimate","approval_status","source_system","source_record_id","ingested_at"],
"vendor_estimate_lines":["estimate_line_id","estimate_id","line_type","quantity","amount"],
"vendor_invoices":["invoice_id","work_order_id","vendor_id","invoice_number","invoice_date","total_invoice","estimate_id","payment_status","source_system","source_record_id","ingested_at"],
"vendor_invoice_lines":["invoice_line_id","invoice_id","line_type","quantity","amount"],
"repair_notes":["repair_note_id","work_order_id","equipment_id","created_at","note_type","source_system","source_record_id","ingested_at"],
"document_artifacts":["document_artifact_id","document_type","file_name","mime_type","content_hash","received_at","extraction_status","retention_class"],
"human_review_tasks":["review_task_id","task_type","priority","entity_type","entity_id","reason","status","assigned_role","created_at"],
}


def load_phase2_data(root: Path) -> dict[str,pd.DataFrame]:
    return {name:pd.read_csv(root / filename) for name,filename in DATASETS.items()}


def _result(dataset:str, rule:str, passed:bool, detail:str, severity:str="ERROR") -> dict[str,Any]:
    return {"dataset":dataset,"rule":rule,"passed":bool(passed),"severity":severity if not passed else "PASS","detail":detail}


def quality_report(root: Path) -> pd.DataFrame:
    d=load_phase2_data(root); out=[]
    for name,df in d.items():
        req=REQUIRED[name]; missing=[c for c in req if c not in df.columns]
        out.append(_result(name,"required_columns",not missing,f"missing={missing}"))
        if missing: continue
        nulls=int(df[req].isna().sum().sum()); out.append(_result(name,"required_values_non_null",nulls==0,f"null_cells={nulls}"))
        key=KEYS[name]; dup=int(df[key].duplicated(keep=False).sum()); out.append(_result(name,"canonical_key_unique",dup==0,f"duplicate_rows={dup}"))
        if {"source_system","source_record_id"}.issubset(df.columns):
            dup=int(df.duplicated(["source_system","source_record_id"],keep=False).sum()); out.append(_result(name,"source_identity_unique",dup==0,f"duplicate_rows={dup}"))
    msg=set(d["communication_messages"]["message_id"]); est=set(d["vendor_estimates"]["estimate_id"]); inv=set(d["vendor_invoices"]["invoice_id"]); docs=set(d["document_artifacts"]["document_artifact_id"])
    for name,col,parent,rule in [("communication_participants","message_id",msg,"message_fk"),("vendor_estimate_lines","estimate_id",est,"estimate_fk"),("vendor_invoice_lines","invoice_id",inv,"invoice_fk")]:
        bad=int((~d[name][col].isin(parent)).sum()); out.append(_result(name,rule,bad==0,f"unresolved={bad}"))
    for name in ["vendor_estimates","vendor_invoices","repair_notes"]:
        for col in ["work_order_id","vendor_id"]:
            if col in d[name]:
                # Foreign keys are allowed to be absent only where the source field is null; present values are validated later against Phase 1 data.
                out.append(_result(name,f"{col}_present_values",d[name][col].notna().all(),f"null_values={int(d[name][col].isna().sum())}","WARNING"))
    vm=d["voicemail_records"]; failed=int((vm["transcription_status"].str.upper()=="FAILED").sum()); out.append(_result("voicemail_records","failed_transcription_review",failed==0,f"failed={failed}","WARNING"))
    da=d["document_artifacts"]; bad_hash=int(da["content_hash"].astype(str).str.len().eq(0).sum()); out.append(_result("document_artifacts","content_hash_present",bad_hash==0,f"missing_hash={bad_hash}"))
    return pd.DataFrame(out)


def reconcile_estimates_invoices(root: Path, tolerance: float=0.01) -> pd.DataFrame:
    d=load_phase2_data(root); e=d["vendor_estimates"]; i=d["vendor_invoices"]
    m=i.merge(e[["estimate_id","total_estimate"]],on="estimate_id",how="left",suffixes=("_invoice","_estimate"))
    m["variance"]=(pd.to_numeric(m["total_invoice"],errors="coerce")-pd.to_numeric(m["total_estimate"],errors="coerce")).round(2)
    m["within_tolerance"]=m["variance"].abs()<=tolerance
    m["review_required"]=~m["within_tolerance"]
    return m[["invoice_id","work_order_id","vendor_id","estimate_id","total_estimate","total_invoice","variance","within_tolerance","review_required"]]


def build_review_queue(root: Path) -> pd.DataFrame:
    d=load_phase2_data(root); rows=[]
    vm=d["voicemail_records"]
    for _,r in vm[vm["transcription_status"].str.upper().eq("FAILED")].iterrows(): rows.append(["TRANSCRIPTION_FAILURE","MEDIUM","voicemail",r["voicemail_id"],"Transcription failed; manual review required","OPEN","FLEET_MAINTENANCE_COORDINATOR"])
    dr=d["driver_requests"]
    for _,r in dr[dr["safety_related"].astype(str).str.lower().eq("true")].iterrows(): rows.append(["SAFETY_REQUEST","CRITICAL","driver_request",r["request_id"],"Safety-related driver request requires human decision","OPEN","FLEET_MAINTENANCE_MANAGER"])
    rec=reconcile_estimates_invoices(root)
    for _,r in rec[rec["review_required"]].iterrows(): rows.append(["INVOICE_VARIANCE","HIGH","vendor_invoice",r["invoice_id"],f"Invoice variance {r['variance']:.2f} against estimate","OPEN","FLEET_MAINTENANCE_MANAGER"])
    return pd.DataFrame(rows,columns=["task_type","priority","entity_type","entity_id","reason","status","assigned_role"])
