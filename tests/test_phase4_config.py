import pytest

from app.integration_config import AuthMode, DEFAULT_SOURCE_CONFIG, SourceConfig, enabled_sources
from app.integrations import IntegrationSource


def test_default_configuration_covers_all_sources():
    assert set(DEFAULT_SOURCE_CONFIG) == set(IntegrationSource)
    assert all(item.auth_mode == AuthMode.SYNTHETIC for item in DEFAULT_SOURCE_CONFIG.values())


def test_disabled_sources_are_excluded():
    config = dict(DEFAULT_SOURCE_CONFIG)
    config[IntegrationSource.ELD] = SourceConfig(IntegrationSource.ELD, enabled=False)
    assert IntegrationSource.ELD not in [item.source for item in enabled_sources(config)]


@pytest.mark.parametrize("field", ["timeout_seconds", "max_attempts", "freshness_hours"])
def test_positive_operational_limits(field):
    kwargs = {field: 0}
    with pytest.raises(ValueError):
        SourceConfig(IntegrationSource.TMT, **kwargs)
