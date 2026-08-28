from datetime import datetime

from tests.conftest import make_event

from app.core.metrics import compute_metrics


def test_agency_kpis_match_rate_and_unmatched(sample_events):
    metrics = compute_metrics(sample_events, category="Agency")
    assert metrics.kpis.total_requests == 2
    assert metrics.kpis.completed_responses == 1
    assert metrics.kpis.unmatched_count == 1
    assert metrics.kpis.match_rate == 50.0
    assert metrics.kpis.avg_duration_seconds == 17.338
    assert metrics.kpis.p95_duration_seconds == 17.338
    assert metrics.kpis.max_duration_seconds == 17.338


def test_idle_hour_has_null_match_rate_not_zero(sample_events):
    metrics = compute_metrics(sample_events, category="SLT")
    idle = [row for row in metrics.hourly if row.started == 0]
    assert idle, "expected hours with no traffic in 24h table"
    assert all(row.match_rate is None for row in idle)


def test_hourly_peak_and_completion_gap(sample_events):
    metrics = compute_metrics(sample_events, category="SLT")
    thirteen = next(row for row in metrics.hourly if row.hour == "13:00")
    assert thirteen.started == 2
    assert thirteen.completed == 2
    assert thirteen.completion_gap == 0
    assert thirteen.match_rate == 100.0


def test_request_type_share_and_per_deal():
    events = [
        make_event(),
        make_event(
            id="trade:SLT:SL_ALTER_TRADE:2",
            display_id="2",
            group_id="HH0Y9V9",
            duration_seconds=20.0,
            start=datetime(2026, 8, 24, 13, 10, 0),
            end=datetime(2026, 8, 24, 13, 10, 20),
        ),
        make_event(
            id="a",
            display_id="3",
            group_id="OTHER",
            workflow="SL_CREATE_TRADE",
            request_type="SLT Trade Creation",
            duration_seconds=10.0,
            start=datetime(2026, 8, 24, 8, 0, 0),
            end=datetime(2026, 8, 24, 8, 0, 10),
        ),
    ]
    metrics = compute_metrics(events, category="SLT")
    settlement = next(r for r in metrics.request_types if r.request_type == "SLT Trade Settlement")
    assert settlement.count == 2
    assert settlement.percent == 66.7
    deal = next(d for d in metrics.per_deal if d.group_id == "HH0Y9V9")
    assert deal.trade_count == 2
    assert deal.min_duration_seconds == 20.0
    assert deal.max_duration_seconds == 76.6


def test_issues_surface_unmatched_fail_retry_slow(sample_events):
    metrics = compute_metrics(sample_events, category=None)
    kinds = {i.kind for i in metrics.issues}
    assert {"unmatched", "fail", "retry", "slow"} <= kinds
    unmatched = next(i for i in metrics.issues if i.kind == "unmatched")
    assert unmatched.event_id == "trade:Agency:AGY_TRADE:2890940"


def test_empty_events_zero_kpis():
    metrics = compute_metrics([], category="Agency")
    assert metrics.kpis.total_requests == 0
    assert metrics.kpis.match_rate is None
    assert metrics.hourly == []
    assert metrics.issues == []
