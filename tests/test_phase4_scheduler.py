from datetime import datetime, timedelta, timezone

from app.integration_config import DEFAULT_SOURCE_CONFIG, SourceConfig
from app.integration_scheduler import build_schedule, schedule_for
from app.integrations import IntegrationSource


NOW = datetime(2026, 8, 7, 12, tzinfo=timezone.utc)


def test_missing_ingestion_is_due():
    result = schedule_for(DEFAULT_SOURCE_CONFIG[IntegrationSource.TMT], None, NOW)
    assert result.due is True
    assert result.reason == "NO_SUCCESSFUL_INGESTION"


def test_recent_ingestion_is_within_sla():
    result = schedule_for(DEFAULT_SOURCE_CONFIG[IntegrationSource.OEM], NOW - timedelta(hours=2), NOW)
    assert result.due is False
    assert result.reason == "WITHIN_SLA"


def test_old_ingestion_is_due():
    result = schedule_for(DEFAULT_SOURCE_CONFIG[IntegrationSource.ELD], NOW - timedelta(hours=25), NOW)
    assert result.due is True
    assert result.reason == "SLA_DUE"


def test_disabled_source_is_not_due():
    config = SourceConfig(IntegrationSource.PFJ, enabled=False)
    result = schedule_for(config, None, NOW)
    assert result.due is False
    assert result.reason == "SOURCE_DISABLED"


def test_build_schedule_covers_all_sources():
    results = build_schedule(DEFAULT_SOURCE_CONFIG, {}, NOW)
    assert {item.source for item in results} == {source.value for source in IntegrationSource}
