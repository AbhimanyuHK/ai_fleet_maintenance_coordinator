"""Safety gate preventing AI workflows from silently using stale integrations."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from app.integration_config import SourceConfig
from app.integration_scheduler import schedule_for


@dataclass(frozen=True)
class FreshnessDecision:
    allowed: bool
    status: str
    blocking_sources: tuple[str, ...]
    reason: str


def evaluate_ai_freshness(
    configs: dict,
    last_ingestions: dict[str, datetime | None],
    required_sources: set[str],
    now: datetime | None = None,
) -> FreshnessDecision:
    current = now or datetime.now(timezone.utc)
    blocking: list[str] = []
    for source in sorted(required_sources):
        config: SourceConfig | None = next((c for c in configs.values() if c.source.value == source), None)
        if config is None or not config.enabled:
            blocking.append(source)
            continue
        schedule = schedule_for(config, last_ingestions.get(source), current)
        if schedule.due:
            blocking.append(source)
    if blocking:
        return FreshnessDecision(False, "BLOCKED", tuple(blocking), "Required integration data is missing or outside its freshness SLA.")
    return FreshnessDecision(True, "READY", (), "Required integration data is within configured freshness SLAs.")
