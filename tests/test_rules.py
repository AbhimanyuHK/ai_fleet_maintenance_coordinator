from datetime import date, datetime, timedelta, timezone

from app.domain import Fault, PMTask, Priority, WorkOrder
from app.rules import fault_alerts, pm_alerts, prioritize, work_order_alerts


def test_pm_due_within_five_days_is_high_priority():
    task = PMTask(pm_id="PM-1", equipment_id="U-1", due_date=date(2026, 8, 10))
    alerts = pm_alerts([task], today=date(2026, 8, 6))
    assert alerts[0].priority == Priority.HIGH


def test_overdue_pm_is_critical():
    task = PMTask(pm_id="PM-2", equipment_id="U-2", due_date=date(2026, 8, 1))
    alerts = pm_alerts([task], today=date(2026, 8, 6))
    assert alerts[0].priority == Priority.CRITICAL


def test_safety_fault_is_critical():
    fault = Fault(
        fault_id="F-1",
        equipment_id="U-3",
        fault_code="BRAKE",
        description="Brake pressure loss",
        safety_related=True,
        first_detected=datetime.now(timezone.utc),
    )
    assert fault_alerts([fault])[0].priority == Priority.CRITICAL


def test_repeated_fault_is_high():
    fault = Fault(
        fault_id="F-2",
        equipment_id="U-4",
        fault_code="ENG",
        repeat_count=3,
        first_detected=datetime.now(timezone.utc),
    )
    assert fault_alerts([fault])[0].priority == Priority.HIGH


def test_work_order_over_thirty_days_is_flagged():
    wo = WorkOrder(
        work_order_id="WO-1",
        equipment_id="U-5",
        opened_at=datetime.now(timezone.utc) - timedelta(days=31),
    )
    alerts = work_order_alerts([wo], now=datetime.now(timezone.utc))
    assert len(alerts) == 1
    assert alerts[0].category == "WORK_ORDER"


def test_prioritization_puts_critical_first():
    task = PMTask(pm_id="PM-3", equipment_id="U-7", due_date=date(2026, 8, 1))
    fault = Fault(
        fault_id="F-3",
        equipment_id="U-6",
        fault_code="SAFE",
        safety_related=True,
        first_detected=datetime.now(timezone.utc),
    )
    alerts = prioritize([*pm_alerts([task], date(2026, 8, 6)), *fault_alerts([fault])])
    assert alerts[0].priority == Priority.CRITICAL
