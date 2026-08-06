from datetime import date, datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class Priority(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class Equipment(BaseModel):
    equipment_id: str
    unit_number: str
    vin: Optional[str] = None
    status: str = "AVAILABLE"
    location: Optional[str] = None
    mileage: int = 0
    engine_hours: float = 0


class PMTask(BaseModel):
    pm_id: str
    equipment_id: str
    due_date: date
    scheduled_date: Optional[date] = None
    status: str = "OPEN"
    vendor: Optional[str] = None
    location: Optional[str] = None


class Fault(BaseModel):
    fault_id: str
    equipment_id: str
    fault_code: str
    description: str = ""
    severity: Priority = Priority.MEDIUM
    first_detected: datetime
    repeat_count: int = Field(default=1, ge=1)
    safety_related: bool = False


class WorkOrder(BaseModel):
    work_order_id: str
    equipment_id: str
    opened_at: datetime
    status: str = "OPEN"
    estimated_cost: float = Field(default=0, ge=0)
    approved_cost: float = Field(default=0, ge=0)
    actual_cost: float = Field(default=0, ge=0)


class MaintenanceAlert(BaseModel):
    equipment_id: str
    category: str
    priority: Priority
    title: str
    reason: str
    recommended_action: str
