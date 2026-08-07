from datetime import datetime, timezone

from app.integration_health import SourceHealth


def test_health_view_has_expected_source_contract():
    health = [
        SourceHealth("TMT", "FRESH", 10, 1, 2, datetime.now(timezone.utc)),
        SourceHealth("OEM", "STALE", 8, 0, 1, datetime.now(timezone.utc)),
        SourceHealth("ELD", "NO_DATA", 0, 0, 0, None),
        SourceHealth("PFJ", "FRESH", 4, 0, 0, datetime.now(timezone.utc)),
        SourceHealth("VENDOR", "OUTDATED", 3, 2, 1, datetime.now(timezone.utc)),
    ]
    assert {item.source for item in health} == {"TMT", "OEM", "ELD", "PFJ", "VENDOR"}
    assert sum(item.rejected for item in health) == 3
    assert sum(item.duplicates for item in health) == 4
