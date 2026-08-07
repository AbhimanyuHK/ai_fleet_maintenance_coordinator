import streamlit as st

st.set_page_config(page_title="Business Guide - Fleet AI Coordinator", page_icon="📘", layout="wide")

st.title("📘 Fleet Maintenance AI Coordinator — Business Guide")
st.caption("A business view of why the coordinator is needed, how AI helps, and where the financial value can come from.")

st.info(
    "This platform is designed to augment fleet maintenance coordinators, not simply replace people. "
    "AI handles repetitive analysis, prioritization, knowledge retrieval and drafting; people retain control "
    "over safety, compliance, financial and return-to-service decisions."
)

st.header("1. Why does a fleet need an AI Coordinator?")
st.markdown("""
A fleet maintenance operation usually has information spread across fleet systems, OEM sources, ELD/telematics,
vendors, driver communications, work orders, PM schedules, invoices and maintenance documents.

The problem is not only **lack of data**. The problem is turning many changing signals into the **right action at the right time**.

Typical business problems:

- PM tasks are missed, delayed or manually chased.
- Faults arrive before a coordinator has time to investigate the full history.
- Safety-related requests can compete with routine maintenance.
- Technicians and coordinators spend time searching manuals, history and prior repairs.
- Vendor estimates and invoices may contain price or scope variances.
- Vehicles can remain unavailable longer because scheduling and communication are fragmented.
- Coordinators spend valuable time copying information between systems and following up with drivers/vendors.
- Management lacks a single view of maintenance risk, backlog, downtime and data quality.
""")

st.header("2. What is the AI Fleet Maintenance Coordinator?")
st.markdown("""
Think of it as a **digital maintenance operations assistant** sitting between the data and the maintenance team.
It continuously brings together the operational picture, checks whether the data is trustworthy, retrieves approved
maintenance knowledge, and prepares explainable recommendations for people to review.
""")

st.code("""Fleet / Enterprise Sources
        ↓
Data Quality + Standardization
        ↓
Integration Health + Freshness Gate
        ↓
Maintenance Knowledge / RAG
        ↓
AI Coordinator
   ├── PM / maintenance recommendations
   ├── Fault and predictive-risk assessment
   ├── Repair recommendations
   ├── Maintenance scheduling suggestions
   ├── Driver / vendor communication drafts
   └── Invoice / estimate review assistance
        ↓
Evidence + Reasoning + Confidence
        ↓
Human Approval
        ↓
Operational Action
        ↓
Outcome / Feedback
""")

st.header("3. How does AI improve the business?")
benefits = [
    ("Preventive maintenance", "Prioritize upcoming/overdue PM work and identify maintenance that deserves attention before it becomes a breakdown.", "Fewer avoidable failures and better fleet availability."),
    ("Fault triage", "Combine fault severity, history, equipment context and safety signals to help coordinators decide what needs attention first.", "Faster response and better use of maintenance capacity."),
    ("Downtime reduction", "Help coordinate repair priority, service location and scheduling around vehicle availability.", "More productive fleet time and less avoidable downtime."),
    ("Technician/coordinator productivity", "Retrieve approved knowledge and summarize relevant history instead of requiring manual searching across systems.", "Less administrative effort and faster preparation."),
    ("Vendor cost control", "Compare estimates/invoices and highlight variances or items requiring review.", "Reduced leakage and better financial oversight."),
    ("Communication", "Classify driver requests and prepare consistent response drafts with the relevant maintenance context.", "Faster communication while keeping humans in control."),
    ("Management visibility", "Present maintenance risk, PM status, backlog, data quality and integration freshness in one place.", "Better decisions based on a common operational picture."),
]
for name, action, value in benefits:
    with st.expander(name):
        st.write(f"**AI assistance:** {action}")
        st.write(f"**Business value:** {value}")

st.header("4. Where does the money come from?")
st.markdown("""
The business case should not be based on an assumed percentage improvement. It should be measured against the fleet's
own baseline. The main value pools are:

1. **Coordinator time recovered** — less manual searching, chasing, copying and report preparation.
2. **Downtime avoided** — fewer preventable breakdowns and shorter maintenance turnaround where the coordinator can act earlier.
3. **Maintenance cost control** — better PM discipline and fewer reactive repairs where the data supports prevention.
4. **Vendor leakage reduction** — earlier visibility into estimate/invoice variances and duplicate or unexpected charges.
5. **Fleet utilization** — better scheduling can return vehicles to productive service sooner.
6. **Risk/compliance protection** — better prioritization of safety and compliance issues can reduce operational exposure.
""")

st.subheader("Illustrative business-case calculator")
st.caption("These are planning assumptions only. Replace them with your actual fleet numbers before making an investment decision.")
c1, c2, c3 = st.columns(3)
with c1:
    coordinators = st.number_input("Maintenance coordinators", min_value=1, value=3, step=1)
    annual_cost = st.number_input("Fully loaded annual cost / coordinator (₹)", min_value=0, value=1200000, step=100000)
with c2:
    hours_week = st.number_input("Hours/week spent on repetitive coordination", min_value=0.0, value=15.0, step=1.0)
    recover_pct = st.slider("Potentially recoverable time (%)", 0, 80, 25)
with c3:
    annual_ai_cost = st.number_input("Estimated annual AI/platform cost (₹)", min_value=0, value=0, step=100000)
    downtime_value = st.number_input("Annual avoidable downtime value to target (₹)", min_value=0, value=0, step=100000)

working_hours = 2080
coord_time_value = coordinators * annual_cost * ((hours_week * 52) / working_hours) * (recover_pct / 100)
illustrative_benefit = coord_time_value + downtime_value
net_value = illustrative_benefit - annual_ai_cost
roi = (net_value / annual_ai_cost * 100) if annual_ai_cost > 0 else None

m1, m2, m3 = st.columns(3)
m1.metric("Illustrative annual value", f"₹{illustrative_benefit:,.0f}")
m2.metric("Illustrative net value", f"₹{net_value:,.0f}")
m3.metric("Illustrative ROI", f"{roi:,.1f}%" if roi is not None else "Set AI cost")
st.warning("Do not treat this calculator as a forecast. Validate coordinator time, downtime cost, repair cost, vendor leakage and AI/platform cost with your actual finance and operations data.")

st.header("5. AI Coordinator vs. Manual Coordination")
st.markdown("""
| Activity | Mostly manual today | AI Coordinator assistance |
|---|---|---|
| PM follow-up | Review schedules and chase tasks | Prioritize due/at-risk PM work |
| Fault investigation | Search several systems | Combine context and summarize evidence |
| Repair decision support | Search history/manuals | Retrieve approved knowledge and recommend options |
| Scheduling | Coordinate availability manually | Suggest priority/time/location based on constraints |
| Driver communication | Read, classify and draft responses | Classify and draft; human approves |
| Vendor review | Compare documents manually | Highlight estimate/invoice variances |
| Risk review | Spreadsheet/report driven | Explainable risk prioritization |
| Management reporting | Manual aggregation | Unified operational view |
""")

st.header("6. What the AI Coordinator should NOT do")
st.error("AI should not independently authorize safety-critical repairs, return-to-service decisions, compliance overrides, financial approvals, or irreversible operational actions.")
st.markdown("""
The intended control model is:

**AI recommends → evidence is shown → human reviews → approved action → outcome is recorded.**

This makes the platform an operational decision-support system rather than an uncontrolled autonomous agent.
""")

st.header("7. Recommended business rollout")
for step, title, detail in [
    ("1", "Baseline", "Measure PM compliance, breakdowns, downtime, coordinator hours, repair cost, vendor leakage and communication workload."),
    ("2", "Start with visibility", "Connect trusted data and expose a common maintenance picture before automating actions."),
    ("3", "Pilot AI assistance", "Start with PM prioritization, knowledge retrieval, communication drafts and repair decision support."),
    ("4", "Measure outcomes", "Compare the pilot with the baseline using operational and financial KPIs."),
    ("5", "Expand carefully", "Add predictive risk, scheduling optimization and deeper integrations only after the data and controls are proven."),
]:
    st.markdown(f"### {step}. {title}\n{detail}")

st.success("Business goal: move the maintenance team from reactive coordination and information chasing toward proactive, evidence-based fleet maintenance decisions.")
