from datetime import date, datetime, timezone

from fastapi import FastAPI
from pydantic import Field

from .domain import Fault, PMTask, WorkOrder
from .services import build_priority_queue

app = FastAPI(title="AI Fleet Maintenance Coordinator", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/maintenance/priority-queue")
def priority_queue(
    pm_tasks: list[PMTask] = Field(default_factory=list),
    faults: list[Fault] = Field(default_factory=list),
    work_orders: list[WorkOrder] = Field(default_factory=list),
) -> dict:
    alerts = build_priority_queue(
        pm_tasks,
        faults,
        work_orders,
        today=date.today(),
        now=datetime.now(timezone.utc),
    )
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "count": len(alerts),
        "alerts": [a.model_dump(mode="json") for a in alerts],
    }
