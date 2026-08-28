import gzip
from datetime import datetime
from pathlib import Path

from tests.conftest import make_event

from app.api.serialize import event_to_public, filter_events, metrics_to_public, run_to_public
from app.core.metrics import compute_metrics
from app.core.models import Run
from app.core.timeline import extract_timeline
from app.core.xlsx_ingest import find_workbook


def test_filter_events_by_hour_deal_and_query(sample_events):
    found = filter_events(sample_events, hour="13:00", category="SLT")
    assert {event.display_id for event in found} == {"786712011", "999000"}
    deal = filter_events(sample_events, group_id="HH0Y9V9")
    assert len(deal) == 1
    search = filter_events(sample_events, q="allocation")
    assert search[0].display_id == "821933"


def test_public_serializers(sample_run):
    public_run = run_to_public(sample_run)
    assert public_run["eventCount"] == 5
    public_event = event_to_public(sample_run.events[0])
    assert public_event["displayId"] == "786712011"
    public_metrics = metrics_to_public(compute_metrics(sample_run.events, "SLT"))
    assert "kpis" in public_metrics
    assert public_metrics["issues"]


def test_gzip_timeline_and_nested_workbook(tmp_path: Path):
    raw = (
        "[2026-06-03 15:24:56,422 EMT-1][786712011][SL_ALTER_TRADE] LDTLINFO "
        "com.example.Service - hello {\"eventId\":\"ALTER_TRADE_786712011\"}\n"
    )
    gz = tmp_path / "a.log.gz"
    with gzip.open(gz, "wt", encoding="utf-8") as handle:
        handle.write(raw)
    hops = extract_timeline("786712011", [str(gz)])
    assert len(hops) == 1
    nested = tmp_path / "reports"
    nested.mkdir()
    xlsx = nested / "trade_analysis.xlsx"
    xlsx.write_bytes(b"not-really-xlsx")
    assert find_workbook(tmp_path) == xlsx
    logs_only = tmp_path / "logs"
    logs_only.mkdir()
    parent_book = tmp_path / "trade_analysis.xlsx"
    parent_book.write_bytes(b"xlsx")
    assert find_workbook(logs_only) == parent_book


def test_run_roundtrip_dict():
    event = make_event()
    run = Run(id="x", domain="trade", source_path="/l", status="completed", events=[event], created_at=datetime(2026, 1, 1))
    restored = Run.from_dict(run.to_dict())
    assert restored.events[0].display_id == event.display_id
