import streamlit as st

st.set_page_config(
    page_title="Fleet AI Coordinator Guide",
    page_icon="📘",
    layout="wide",
)

st.title("📘 Fleet Maintenance AI Coordinator — Business Guide")
st.caption("A simple view of what the coordinator does, why it matters, and how AI supports fleet maintenance teams.")

st.info(
    "The AI Fleet Maintenance Coordinator is a decision-support layer for fleet maintenance operations. "
    "It brings maintenance data together, identifies what needs attention, explains why, and helps the team "
    "prepare the next action. AI recommends; people remain accountable for safety-critical and operational decisions."
)

st.header("1. What problem are we solving?")
cols = st.columns(4)
for col, title, text in [
    (cols[0], "Too much manual coordination", "Teams spend time checking PM schedules, faults, work orders, driver messages, vendors, and invoices across different sources."),
    (cols[1], "Important signals get missed", "A fault, overdue PM, driver complaint, repair note, or campaign may be viewed separately instead of as one fleet story."),
    (cols[2], "Maintenance decisions take time", "People need to collect evidence before deciding what to inspect, repair, schedule, escalate, or communicate."),
    (cols[3], "Cost and downtime leakage", "Late PMs, repeat repairs, invoice variance, poor vendor decisions, and avoidable downtime can increase operating cost."),
]:
    with col:
        st.subheader(title)
        st.write(text)

st.header("2. What is an AI Fleet Maintenance Coordinator?")
st.write(
    "Think of it as a digital maintenance coordinator that continuously organizes evidence and prepares work for the human team. "
    "It is not a replacement for the maintenance manager, technician, safety process, or approval authority."
)

st.code("""Fleet / Enterprise Sources
        │
        ├── Equipment & PM schedules
        ├── Faults & telemetry events
        ├── Work orders & repair history
        ├── Driver requests & communications
        ├── Vendors, estimates & invoices
        ├── OEM campaigns / recalls
        └── Compliance information
        │
        ▼
Data Foundation & Quality
        │
        ▼
Integration Health + Freshness Gate
        │
        ▼
Knowledge + RAG + AI Reasoning
        │
        ├── Maintenance recommendation
        ├── Repair recommendation
        ├── PM scheduling recommendation
        ├── Predictive risk assessment
        └── Communication assistance
        │
        ▼
Human Review / Approval
        │
        ▼
Operational Action + Feedback
""", language="text")

st.header("3. How does AI help with PM schedules?")
st.write("The coordinator does not simply look at a calendar. It combines PM rules with operational context.")
st.markdown(
    """
- **Find due or overdue PMs** from the trusted PM schedule.
- **Check vehicle availability** so a recommendation does not ignore current operational constraints.
- **Consider recent faults and maintenance history** to identify relevant context.
- **Use approved maintenance knowledge** to explain what should be inspected or considered.
- **Recommend a practical maintenance window** based on the available evidence.
- **Surface the reason and supporting evidence** to the maintenance team.
- **Require human approval** before a consequential operational action is taken.
"""
)

with st.expander("Example: overdue PM"):
    st.markdown(
        "**Situation:** Vehicle EQ-104 has an overdue PM, a recent high-severity fault, and is scheduled for an upcoming route.\n\n"
        "**Coordinator:** Flags the PM, combines the fault and maintenance history, checks availability, and prepares a recommendation.\n\n"
        "**Human:** Reviews the evidence and approves, changes, or rejects the proposed maintenance timing."
    )

st.header("4. What other maintenance problems can it coordinate?")
items = [
    ("🚨 Fault & risk", "Prioritize significant faults, identify safety-related signals, and explain the evidence behind a risk assessment."),
    ("🔧 Repair decisions", "Combine fault information, repair history, notes, approved knowledge, and vendor information to support repair recommendations."),
    ("📅 Maintenance scheduling", "Turn PM and maintenance needs into scheduling recommendations while considering availability and operational constraints."),
    ("💬 Driver communication", "Classify driver requests and communications, identify urgent items, and draft responses for human review."),
    ("💰 Vendor & invoice control", "Compare estimates and invoices, identify variance, and route suspicious or important cases to human review."),
    ("📚 Maintenance knowledge", "Search approved OEM/company knowledge and provide grounded answers with supporting evidence rather than unsupported guesses."),
]
for title, description in items:
    with st.container(border=True):
        st.subheader(title)
        st.write(description)

st.header("5. What makes this different from a generic chatbot?")
left, right = st.columns(2)
with left:
    st.subheader("Generic chatbot")
    st.markdown("""
- Starts with a question
- May lack current fleet context
- May not know whether data is stale
- Can produce plausible but unsupported answers
- Usually does not enforce maintenance workflow controls
""")
with right:
    st.subheader("AI Fleet Maintenance Coordinator")
    st.markdown("""
- Starts with trusted operational data
- Checks data quality and integration freshness
- Uses approved maintenance knowledge / RAG
- Shows evidence and reasoning context
- Applies workflow-specific readiness rules
- Keeps human approval in the operational loop
""")

st.header("6. Human-in-the-loop is intentional")
st.warning(
    "AI is the intelligence layer, not the authority layer. Safety-critical, compliance-sensitive, financial, "
    "return-to-service, and other consequential decisions remain subject to deterministic controls and required human approval."
)

st.header("7. What the business can expect")
metrics = st.columns(5)
for col, value, label in [
    (metrics[0], "↓", "Manual coordination effort"),
    (metrics[1], "↑", "Maintenance visibility"),
    (metrics[2], "↑", "Decision consistency"),
    (metrics[3], "↓", "Avoidable downtime / leakage"),
    (metrics[4], "↑", "Evidence-based decisions"),
]:
    col.metric(label, value)

st.caption(
    "These are target business outcomes, not measured production results yet. The current application uses synthetic/demo data "
    "and is intended to demonstrate the operating model before live enterprise integrations are introduced."
)

st.header("8. Recommended rollout")
st.markdown(
    """
**Step 1 — Trust the data:** establish canonical fleet, PM, fault, work-order, vendor, communication, and compliance data.  
**Step 2 — Connect the enterprise:** integrate TMT, OEM, ELD, PFJ, and vendor sources behind controlled contracts.  
**Step 3 — Start with decision support:** use RAG and AI recommendations with evidence and human approval.  
**Step 4 — Measure outcomes:** track PM adherence, downtime, repeat repairs, invoice leakage, response time, and recommendation acceptance.  
**Step 5 — Expand carefully:** introduce predictive maintenance and optimization only after data quality, integration reliability, and governance are proven.
"""
)

st.success("Business takeaway: the coordinator does not replace the maintenance team — it gives the team the right information, context, recommendations, and evidence at the right time.")
