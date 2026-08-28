from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any


def _parse_dt(value: Any) -> datetime | None:
    if value in (None, ""):
        return None
    if isinstance(value, datetime):
        return value
    text = str(value).replace("T", " ").strip()
    for fmt in ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue
    return None


@dataclass
class Event:
    id: str
    domain: str
    display_id: str
    group_id: str
    category: str
    workflow: str
    request_type: str
    status: str
    outcome: str | None
    start: datetime | None
    end: datetime | None
    duration_seconds: float | None
    request_count: int
    response_count: int
    request_files: list[str]
    response_files: list[str]
    request_payload: str | None
    response_payload: str | None
    tags: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["start"] = self.start.isoformat() if self.start else None
        data["end"] = self.end.isoformat() if self.end else None
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Event:
        payload = dict(data)
        payload["start"] = _parse_dt(payload.get("start"))
        payload["end"] = _parse_dt(payload.get("end"))
        payload["tags"] = payload.get("tags") or {}
        return cls(**payload)


@dataclass
class Hop:
    timestamp: datetime | None
    thread: str | None
    service: str | None
    workflow: str | None
    level: str | None
    summary: str
    payload: str | None
    source_file: str
    gap_seconds: float | None

    def to_public(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(sep=" ") if self.timestamp else None,
            "thread": self.thread,
            "service": self.service,
            "workflow": self.workflow,
            "level": self.level,
            "summary": self.summary,
            "payload": self.payload,
            "sourceFile": self.source_file,
            "gapSeconds": self.gap_seconds,
        }


@dataclass
class Kpis:
    total_requests: int
    completed_responses: int
    unmatched_count: int
    match_rate: float | None
    avg_duration_seconds: float | None
    p95_duration_seconds: float | None
    max_duration_seconds: float | None


@dataclass
class HourlyRow:
    hour: str
    started: int
    completed: int
    avg_duration_seconds: float | None
    match_rate: float | None
    completion_gap: int


@dataclass
class RequestTypeRow:
    request_type: str
    count: int
    percent: float


@dataclass
class DealRow:
    group_id: str
    trade_count: int
    min_duration_seconds: float | None
    max_duration_seconds: float | None
    avg_duration_seconds: float | None


@dataclass
class Issue:
    kind: str
    event_id: str
    display_id: str
    summary: str


@dataclass
class MetricSnapshot:
    category: str | None
    kpis: Kpis
    hourly: list[HourlyRow]
    request_types: list[RequestTypeRow]
    per_deal: list[DealRow]
    issues: list[Issue]


@dataclass
class Run:
    id: str
    domain: str
    source_path: str
    status: str
    events: list[Event]
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "domain": self.domain,
            "source_path": self.source_path,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "events": [event.to_dict() for event in self.events],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Run:
        return cls(
            id=data["id"],
            domain=data["domain"],
            source_path=data["source_path"],
            status=data["status"],
            created_at=_parse_dt(data.get("created_at")) or datetime.utcnow(),
            events=[Event.from_dict(item) for item in data.get("events", [])],
        )
