from datetime import date, datetime, timezone

from fastapi import FastAPI

from .domain import Fault, PMTask, WorkOrder
from .rules import fault_alerts, pm_alerts, prioritize, work_order_alerts

app = FastAPI(title="AI Fleet Maintenance Coordinator", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/maintenance/priority-queue")
def priority_queue(
    pm_tasks: list[PMTask] = [],
    faults: list[Fault] = [],
    work_orders: list[WorkOrder] = [],
) -> dict:
    alerts = [
        *pm_alerts(pm_tasks, today=date.today()),
        *fault_alerts(faults),
        *work_order_alerts(work_orders, now=datetime.now(timezone.utc)),
    ]
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "count": len(alerts),
        "alerts": [a.model_dump(mode="json") for a in prioritize(alerts)],
    }
