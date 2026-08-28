from __future__ import annotations

from app.core.metrics import compute_metrics
from app.core.models import Event, MetricSnapshot, Run


def event_to_public(event: Event) -> dict:
    return {
        "id": event.id,
        "domain": event.domain,
        "displayId": event.display_id,
        "groupId": event.group_id,
        "category": event.category,
        "workflow": event.workflow,
        "requestType": event.request_type,
        "status": event.status,
        "outcome": event.outcome,
        "start": event.start.isoformat(sep=" ") if event.start else None,
        "end": event.end.isoformat(sep=" ") if event.end else None,
        "durationSeconds": event.duration_seconds,
        "requestCount": event.request_count,
        "responseCount": event.response_count,
        "requestFiles": event.request_files,
        "responseFiles": event.response_files,
        "requestPayload": event.request_payload,
        "responsePayload": event.response_payload,
        "tags": event.tags,
    }


def run_to_public(run: Run) -> dict:
    return {
        "id": run.id,
        "domain": run.domain,
        "sourcePath": run.source_path,
        "status": run.status,
        "createdAt": run.created_at.isoformat(),
        "eventCount": len(run.events),
    }


def metrics_to_public(snapshot: MetricSnapshot) -> dict:
    return {
        "category": snapshot.category,
        "kpis": {
            "totalRequests": snapshot.kpis.total_requests,
            "completedResponses": snapshot.kpis.completed_responses,
            "unmatchedCount": snapshot.kpis.unmatched_count,
            "matchRate": snapshot.kpis.match_rate,
            "avgDurationSeconds": snapshot.kpis.avg_duration_seconds,
            "p95DurationSeconds": snapshot.kpis.p95_duration_seconds,
            "maxDurationSeconds": snapshot.kpis.max_duration_seconds,
        },
        "hourly": [
            {
                "hour": row.hour,
                "started": row.started,
                "completed": row.completed,
                "avgDurationSeconds": row.avg_duration_seconds,
                "matchRate": row.match_rate,
                "completionGap": row.completion_gap,
            }
            for row in snapshot.hourly
        ],
        "requestTypes": [
            {
                "requestType": row.request_type,
                "count": row.count,
                "percent": row.percent,
            }
            for row in snapshot.request_types
        ],
        "perDeal": [
            {
                "groupId": row.group_id,
                "tradeCount": row.trade_count,
                "minDurationSeconds": row.min_duration_seconds,
                "maxDurationSeconds": row.max_duration_seconds,
                "avgDurationSeconds": row.avg_duration_seconds,
            }
            for row in snapshot.per_deal
        ],
        "issues": [
            {
                "kind": issue.kind,
                "eventId": issue.event_id,
                "displayId": issue.display_id,
                "summary": issue.summary,
            }
            for issue in snapshot.issues
        ],
    }


def filter_events(
    events: list[Event],
    *,
    category: str | None = None,
    status: str | None = None,
    group_id: str | None = None,
    hour: str | None = None,
    q: str | None = None,
) -> list[Event]:
    result = events
    if category:
        result = [event for event in result if event.category == category]
    if status:
        result = [event for event in result if event.status == status]
    if group_id:
        result = [event for event in result if event.group_id == group_id]
    if hour:
        hour_num = int(hour.split(":")[0])
        result = [event for event in result if event.start and event.start.hour == hour_num]
    if q:
        needle = q.lower()
        result = [
            event
            for event in result
            if needle in event.display_id.lower()
            or needle in event.group_id.lower()
            or needle in event.workflow.lower()
            or needle in event.request_type.lower()
        ]
    return result


def snapshot_for(run: Run, category: str | None) -> dict:
    return metrics_to_public(compute_metrics(run.events, category))
