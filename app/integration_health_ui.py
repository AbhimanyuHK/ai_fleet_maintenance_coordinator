"""Streamlit component for the Phase 4 Integration Health view."""
from __future__ import annotations

import pandas as pd
import streamlit as st

from app.integration_health import SourceHealth


def render_integration_health(health: list[SourceHealth]) -> None:
    """Render a business-facing integration health dashboard."""
    st.subheader("Integration Health")
    st.caption("Operational view of TMT, OEM, ELD, PFJ and vendor data freshness and ingestion quality.")

    if not health:
        st.info("No integration health data is available.")
        return

    status_counts = pd.Series([item.freshness for item in health]).value_counts()
    metrics = st.columns(5)
    for index, source in enumerate(health[:5]):
        metrics[index].metric(source.source, source.freshness)

    rows = []
    for item in health:
        rows.append(
            {
                "Source": item.source,
                "Freshness": item.freshness,
                "Accepted": item.accepted,
                "Rejected": item.rejected,
                "Duplicates": item.duplicates,
                "Last ingestion": item.last_ingestion.isoformat() if item.last_ingestion else "Never",
            }
        )

    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    left, right = st.columns(2)
    with left:
        st.markdown("**Freshness distribution**")
        st.bar_chart(status_counts)
    with right:
        st.markdown("**Data quality summary**")
        st.metric("Rejected records", sum(item.rejected for item in health))
        st.metric("Duplicate records skipped", sum(item.duplicates for item in health))

    unhealthy = [item.source for item in health if item.freshness in {"STALE", "OUTDATED", "NO_DATA"}]
    if unhealthy:
        st.warning("Sources requiring attention: " + ", ".join(unhealthy))
    else:
        st.success("All integration sources are currently fresh.")

    st.info("This dashboard is monitoring-only. It does not modify source systems or trigger maintenance actions.")
