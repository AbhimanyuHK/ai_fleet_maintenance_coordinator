from datetime import datetime, timedelta, timezone

from app.ai_freshness_gate import evaluate_ai_freshness
from app.integration_config import DEFAULT_SOURCE_CONFIG
from app.integrations import IntegrationSource

NOW = datetime(2026, 8, 7, 12, tzinfo=timezone.utc)


def test_gate_allows_fresh_required_sources():
    last = {IntegrationSource.OEM.value: NOW - timedelta(hours=1)}
    decision = evaluate_ai_freshness(DEFAULT_SOURCE_CONFIG, last, {IntegrationSource.OEM.value}, NOW)
    assert decision.allowed is True
    assert decision.status == "READY"
    assert decision.blocking_sources == ()


def test_gate_blocks_missing_source():
    decision = evaluate_ai_freshness(DEFAULT_SOURCE_CONFIG, {}, {IntegrationSource.ELD.value}, NOW)
    assert decision.allowed is False
    assert decision.status == "BLOCKED"
    assert decision.blocking_sources == (IntegrationSource.ELD.value,)


def test_gate_blocks_stale_source():
    last = {IntegrationSource.TMT.value: NOW - timedelta(hours=25)}
    decision = evaluate_ai_freshness(DEFAULT_SOURCE_CONFIG, last, {IntegrationSource.TMT.value}, NOW)
    assert decision.allowed is False
    assert decision.blocking_sources == (IntegrationSource.TMT.value,)


def test_gate_requires_enabled_configuration():
    config = dict(DEFAULT_SOURCE_CONFIG)
    config[IntegrationSource.PFJ] = config[IntegrationSource.PFJ].__class__(IntegrationSource.PFJ, enabled=False)
    last = {IntegrationSource.PFJ.value: NOW}
    decision = evaluate_ai_freshness(config, last, {IntegrationSource.PFJ.value}, NOW)
    assert decision.allowed is False
