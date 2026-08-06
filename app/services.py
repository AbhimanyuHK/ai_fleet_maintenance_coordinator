from datetime import date, datetime, timezone

from .domain import Fault, PMTask, WorkOrder
from .rules import fault_alerts, pm_alerts, prioritize, work_order_alerts


def build_priority_queue(
    pm_tasks: list[PMTask],
    faults: list[Fault],
    work_orders: list[WorkOrder],
    today: date | None = None,
    now: datetime | None = None,
) -> list:
    today = today or date.today()
    now = now or datetime.now(timezone.utc)
    alerts = [
        *pm_alerts(pm_tasks, today),
        *fault_alerts(faults),
        *work_order_alerts(work_orders, now),
    ]
    return prioritize(alerts)
