"""Scheduling policy for source ingestion without executing external jobs."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from app.integration_config import SourceConfig


@dataclass(frozen=True)
class SourceSchedule:
    source: str
    enabled: bool
    interval_hours: int
    due: bool
    reason: str


def schedule_for(config: SourceConfig, last_ingestion: datetime | None, now: datetime | None = None) -> SourceSchedule:
    current = now or datetime.now(timezone.utc)
    interval = config.freshness_hours
    if not config.enabled:
        return SourceSchedule(config.source.value, False, interval, False, "SOURCE_DISABLED")
    if last_ingestion is None:
        return SourceSchedule(config.source.value, True, interval, True, "NO_SUCCESSFUL_INGESTION")
    due = current >= last_ingestion + timedelta(hours=interval)
    return SourceSchedule(config.source.value, True, interval, due, "SLA_DUE" if due else "WITHIN_SLA")


def build_schedule(configs: dict, last_ingestions: dict[str, datetime | None], now: datetime | None = None) -> list[SourceSchedule]:
    return [schedule_for(config, last_ingestions.get(config.source.value), now) for config in configs.values()]
