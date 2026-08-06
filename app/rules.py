from datetime import date, datetime, timezone
from typing import Iterable

from .domain import Fault, MaintenanceAlert, PMTask, Priority, WorkOrder


def pm_alerts(tasks: Iterable[PMTask], today: date | None = None) -> list[MaintenanceAlert]:
    today = today or date.today()
    alerts: list[MaintenanceAlert] = []
    for task in tasks:
        if task.status.upper() in {"COMPLETED", "CANCELLED"}:
            continue
        days = (task.due_date - today).days
        if days < 0:
            priority = Priority.CRITICAL
            title = "PM overdue"
            action = "Escalate and schedule immediately."
        elif days <= 5:
            priority = Priority.HIGH
            title = "PM requires immediate scheduling"
            action = "Schedule service before the due date."
        elif days <= 14:
            priority = Priority.MEDIUM
            title = "PM approaching"
            action = "Plan service proactively."
        else:
            continue
        alerts.append(MaintenanceAlert(
            equipment_id=task.equipment_id,
            category="PM",
            priority=priority,
            title=title,
            reason=f"PM {task.pm_id} is due in {days} day(s).",
            recommended_action=action,
        ))
    return alerts


def fault_alerts(faults: Iterable[Fault]) -> list[MaintenanceAlert]:
    alerts: list[MaintenanceAlert] = []
    for fault in faults:
        if fault.safety_related or fault.severity == Priority.CRITICAL:
            priority = Priority.CRITICAL
        elif fault.severity == Priority.HIGH or fault.repeat_count >= 3:
            priority = Priority.HIGH
        elif fault.severity == Priority.MEDIUM:
            priority = Priority.MEDIUM
        else:
            priority = Priority.LOW
        alerts.append(MaintenanceAlert(
            equipment_id=fault.equipment_id,
            category="FAULT",
            priority=priority,
            title=f"Fault {fault.fault_code} requires {priority.value} attention",
            reason=fault.description or "Fault detected by an integrated equipment source.",
            recommended_action=(
                "Immediate safety review; do not dispatch if company policy requires a safety hold."
                if priority == Priority.CRITICAL else
                "Review fault history and develop a maintenance plan."
            ),
        ))
    return alerts


def work_order_alerts(work_orders: Iterable[WorkOrder], now: datetime | None = None) -> list[MaintenanceAlert]:
    now = now or datetime.now(timezone.utc)
    alerts: list[MaintenanceAlert] = []
    for wo in work_orders:
        if wo.status.upper() in {"COMPLETED", "CLOSED", "CANCELLED"}:
            continue
        opened = wo.opened_at
        if opened.tzinfo is None:
            opened = opened.replace(tzinfo=timezone.utc)
        age = (now - opened).days
        if age > 30:
            alerts.append(MaintenanceAlert(
                equipment_id=wo.equipment_id,
                category="WORK_ORDER",
                priority=Priority.HIGH,
                title="Work order older than 30 days",
                reason=f"Work order {wo.work_order_id} has been open for {age} days.",
                recommended_action="Add a delay explanation and escalate according to policy.",
            ))
    return alerts


def prioritize(alerts: Iterable[MaintenanceAlert]) -> list[MaintenanceAlert]:
    rank = {Priority.CRITICAL: 0, Priority.HIGH: 1, Priority.MEDIUM: 2, Priority.LOW: 3}
    return sorted(alerts, key=lambda a: (rank[a.priority], a.equipment_id, a.category))
