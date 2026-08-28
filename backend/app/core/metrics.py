from __future__ import annotations

import math
from collections import defaultdict

from app.core.models import DealRow, Event, HourlyRow, Issue, Kpis, MetricSnapshot, RequestTypeRow

SLOW_SECONDS = 90.0


def _pct(values: list[float], percentile: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, math.ceil(percentile / 100 * len(ordered)) - 1))
    return ordered[index]


def _round(value: float | None, digits: int = 3) -> float | None:
    if value is None:
        return None
    return round(value, digits)


def compute_metrics(events: list[Event], category: str | None) -> MetricSnapshot:
    scoped = [event for event in events if category is None or event.category == category]
    if not scoped:
        return MetricSnapshot(
            category=category,
            kpis=Kpis(0, 0, 0, None, None, None, None),
            hourly=[],
            request_types=[],
            per_deal=[],
            issues=[],
        )

    matched = [event for event in scoped if event.status == "Matched"]
    unmatched = [event for event in scoped if event.status == "Unmatched"]
    durations = [event.duration_seconds for event in scoped if event.duration_seconds is not None]
    total = len(scoped)
    completed = len(matched)
    kpis = Kpis(
        total_requests=total,
        completed_responses=completed,
        unmatched_count=len(unmatched),
        match_rate=round(completed / total * 100, 1) if total else None,
        avg_duration_seconds=_round(sum(durations) / len(durations), 3) if durations else None,
        p95_duration_seconds=_round(_pct(durations, 95), 3),
        max_duration_seconds=_round(max(durations), 3) if durations else None,
    )

    by_hour: dict[str, list[Event]] = defaultdict(list)
    for event in scoped:
        if event.start:
            by_hour[f"{event.start.hour:02d}:00"].append(event)

    hourly: list[HourlyRow] = []
    for hour_num in range(24):
        label = f"{hour_num:02d}:00"
        bucket = by_hour.get(label, [])
        started = len(bucket)
        done = sum(1 for event in bucket if event.status == "Matched")
        bucket_durations = [event.duration_seconds for event in bucket if event.duration_seconds is not None]
        hourly.append(
            HourlyRow(
                hour=label,
                started=started,
                completed=done,
                avg_duration_seconds=_round(sum(bucket_durations) / len(bucket_durations), 1)
                if bucket_durations
                else None,
                match_rate=round(done / started * 100, 1) if started else None,
                completion_gap=done - started,
            )
        )

    type_counts: dict[str, int] = defaultdict(int)
    for event in scoped:
        type_counts[event.request_type] += 1
    request_types = [
        RequestTypeRow(
            request_type=name,
            count=count,
            percent=round(count / total * 100, 1),
        )
        for name, count in sorted(type_counts.items(), key=lambda item: (-item[1], item[0]))
    ]

    deals: dict[str, list[Event]] = defaultdict(list)
    for event in scoped:
        deals[event.group_id].append(event)
    per_deal: list[DealRow] = []
    for group_id, members in deals.items():
        member_durations = [event.duration_seconds for event in members if event.duration_seconds is not None]
        per_deal.append(
            DealRow(
                group_id=group_id,
                trade_count=len(members),
                min_duration_seconds=_round(min(member_durations), 1) if member_durations else None,
                max_duration_seconds=_round(max(member_durations), 1) if member_durations else None,
                avg_duration_seconds=_round(sum(member_durations) / len(member_durations), 1)
                if member_durations
                else None,
            )
        )
    per_deal.sort(key=lambda row: (-row.trade_count, row.group_id))

    issues: list[Issue] = []
    for event in scoped:
        if event.status == "Unmatched":
            issues.append(Issue("unmatched", event.id, event.display_id, "No matching response"))
        if event.outcome == "FAIL":
            issues.append(Issue("fail", event.id, event.display_id, "Outcome FAIL"))
        if event.request_count > 1:
            issues.append(Issue("retry", event.id, event.display_id, f"Request count {event.request_count}"))
        if event.duration_seconds is not None and event.duration_seconds >= SLOW_SECONDS:
            issues.append(
                Issue("slow", event.id, event.display_id, f"Duration {event.duration_seconds:.1f}s")
            )

    return MetricSnapshot(
        category=category,
        kpis=kpis,
        hourly=hourly,
        request_types=request_types,
        per_deal=per_deal,
        issues=issues,
    )
