"""Phase 4 orchestration primitives for safe external-source ingestion.

The orchestrator is deliberately connector-agnostic. It coordinates existing
adapters, retries transient failures, records outcomes, and never authorizes
maintenance actions.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from app.integration_pipeline import IntegrationStore
from app.integrations import IntegrationAdapter


@dataclass(frozen=True)
class SourceRunResult:
    source: str
    status: str
    attempts: int
    accepted: int
    error: str = ""


class IntegrationOrchestrator:
    def __init__(self, store: IntegrationStore, max_attempts: int = 3):
        if max_attempts < 1:
            raise ValueError("max_attempts must be >= 1")
        self.store = store
        self.max_attempts = max_attempts

    def run_source(
        self,
        adapter: IntegrationAdapter,
        fetch: Callable[[], object] | None = None,
    ) -> SourceRunResult:
        fetch_fn = fetch or adapter.fetch
        last_error = ""
        for attempt in range(1, self.max_attempts + 1):
            try:
                batch = fetch_fn()
                accepted = self.store.ingest(adapter, batch.records)
                return SourceRunResult(
                    source=adapter.source.value,
                    status="SUCCESS",
                    attempts=attempt,
                    accepted=accepted,
                )
            except (ConnectionError, TimeoutError, OSError, ValueError) as exc:
                last_error = str(exc)
        return SourceRunResult(
            source=adapter.source.value,
            status="FAILED",
            attempts=self.max_attempts,
            accepted=0,
            error=last_error,
        )

    def run_all(self, adapters: dict) -> list[SourceRunResult]:
        return [self.run_source(adapter) for adapter in adapters.values()]
