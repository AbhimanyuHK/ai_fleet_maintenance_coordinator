"""Configuration contracts for external fleet-data integrations."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from app.integrations import IntegrationSource


class AuthMode(str, Enum):
    SYNTHETIC = "SYNTHETIC"
    API_KEY = "API_KEY"
    OAUTH2 = "OAUTH2"
    SERVICE_ACCOUNT = "SERVICE_ACCOUNT"


@dataclass(frozen=True)
class SourceConfig:
    source: IntegrationSource
    enabled: bool = True
    timeout_seconds: int = 30
    max_attempts: int = 3
    freshness_hours: int = 24
    auth_mode: AuthMode = AuthMode.SYNTHETIC

    def __post_init__(self) -> None:
        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        if self.max_attempts <= 0:
            raise ValueError("max_attempts must be positive")
        if self.freshness_hours <= 0:
            raise ValueError("freshness_hours must be positive")


DEFAULT_SOURCE_CONFIG: dict[IntegrationSource, SourceConfig] = {
    source: SourceConfig(source=source) for source in IntegrationSource
}


def enabled_sources(config: dict[IntegrationSource, SourceConfig]) -> list[SourceConfig]:
    return [item for item in config.values() if item.enabled]
