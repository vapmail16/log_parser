from datetime import datetime

from tests.conftest import make_event

from app.core.metrics import compute_metrics


def test_regression_idle_hours_are_not_zero_percent_match():
    """Excel charted 0% match on empty hours. That is 'no traffic', not failure."""
    events = [
        make_event(start=datetime(2026, 8, 24, 13, 0, 0), end=datetime(2026, 8, 24, 13, 1, 0), duration_seconds=10.0)
    ]
    hourly = compute_metrics(events, category="SLT").hourly
    empty = next(row for row in hourly if row.hour == "08:00")
    assert empty.started == 0
    assert empty.match_rate is None


def test_regression_p95_not_just_average():
    events = [
        make_event(
            id=f"t{i}",
            display_id=str(i),
            duration_seconds=10.0 + i,
            start=datetime(2026, 8, 24, 13, 0, i),
            end=datetime(2026, 8, 24, 13, 1, i),
        )
        for i in range(10)
    ]
    events.append(
        make_event(
            id="slow",
            display_id="slow",
            duration_seconds=140.0,
            start=datetime(2026, 8, 24, 14, 0, 0),
            end=datetime(2026, 8, 24, 14, 2, 20),
        )
    )
    kpis = compute_metrics(events, category="SLT").kpis
    assert kpis.max_duration_seconds == 140.0
    assert kpis.p95_duration_seconds >= kpis.avg_duration_seconds
