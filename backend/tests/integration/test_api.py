from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from openpyxl import Workbook

from app.main import create_app


def _write_demo(folder: Path) -> None:
    log = folder / "ldtl-trading-2026-08-24.0.log"
    log.write_text(
        "[2026-08-24 13:04:47,982 EMT-1][786712011][SL_ALTER_TRADE] LDTLINFO "
        "com.barclays.ldtl.trading.service.EMTService - sendEMTMessage() EMT Request Message\n"
        "[2026-08-24 13:06:04,558 EMT-1][786712011][SL_ALTER_TRADE] LDTLINFO "
        "com.barclays.ldtl.trading.service.EMTService - EMT Response Message: Sent\n",
        encoding="utf-8",
    )
    wb = Workbook()
    slt = wb.active
    slt.title = "SLT"
    slt.append(
        [
            "Workflow",
            "Request Type",
            "Trade ID",
            "Deal ID",
            "Status",
            "Processing Start",
            "Response Time",
            "Duration Seconds",
            "Request Count",
            "Response Count",
            "Request Source Files",
            "Response Source Files",
            "Request Payload",
            "Response Payload",
            "Outcome",
        ]
    )
    slt.append(
        [
            "SL_ALTER_TRADE",
            "SLT Trade Settlement",
            "786712011",
            "HH0Y9V9",
            "Matched",
            "2026-08-24 13:04:47.982",
            "2026-08-24 13:06:04.558",
            76.576,
            1,
            1,
            str(log),
            str(log),
            "{}",
            'success="true"',
            "SUCCESS",
        ]
    )
    agency = wb.create_sheet("Agency")
    agency.append(
        [
            "Trade ID",
            "Deal ID",
            "Status",
            "Processing Start",
            "Response Time",
            "Duration Seconds",
            "Request Count",
            "Response Count",
            "Request Source Files",
            "Response Source Files",
            "Request Payload",
            "Response Payload",
            "Outcome",
        ]
    )
    agency.append(
        [
            "2890940",
            "UVGMWGKV",
            "Unmatched",
            "2026-08-24 05:10:00.000",
            None,
            None,
            1,
            0,
            str(log),
            "",
            "{}",
            "",
            None,
        ]
    )
    wb.save(folder / "trade_analysis.xlsx")


@pytest.fixture
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    store = tmp_path / "store"
    sample = tmp_path / "sample"
    sample.mkdir()
    _write_demo(sample)
    monkeypatch.setenv("STORE_DIR", str(store))
    monkeypatch.setenv("SAMPLE_SOURCE_DIR", str(sample))
    demo = Path(__file__).resolve().parents[2] / "scripts" / "trade_analysis_demo.py"
    monkeypatch.setenv("TRADE_PARSER_SCRIPT", str(demo))
    return TestClient(create_app())


def test_health_and_domains(client: TestClient):
    health = client.get("/api/health").json()
    assert health["status"] == "ok"
    assert "samplePath" in health
    assert health["parserScript"].endswith("trade_analysis_demo.py")
    assert health["usingLocalParser"] is False
    domains = client.get("/api/domains").json()
    assert domains[0]["id"] == "trade"
    assert domains[1]["id"] == "notification"


def test_sample_run_metrics_events_timeline(client: TestClient):
    created = client.post("/api/runs/sample")
    assert created.status_code == 201
    latest = client.get("/api/runs/latest").json()
    assert latest["domain"] == "trade"
    assert latest["eventCount"] >= 2

    agency = client.get("/api/runs/latest/metrics", params={"category": "Agency"}).json()
    assert agency["kpis"]["unmatchedCount"] == 1
    slt = client.get("/api/runs/latest/metrics", params={"category": "SLT"}).json()
    assert slt["kpis"]["totalRequests"] >= 1

    events = client.get("/api/runs/latest/events", params={"status": "Unmatched"}).json()
    assert events["items"][0]["displayId"] == "2890940"

    event_id = "trade:SLT:SL_ALTER_TRADE:786712011"
    detail = client.get(f"/api/runs/latest/events/{event_id}").json()
    assert detail["groupId"] == "HH0Y9V9"
    hops = client.get(f"/api/runs/latest/events/{event_id}/timeline").json()
    assert len(hops["hops"]) == 2
    assert "EMTService" in hops["hops"][0]["service"]


def test_analyze_accepts_slash_backend_demo_logs_path(monkeypatch: pytest.MonkeyPatch):
    from pathlib import Path as P

    logs = P(__file__).resolve().parents[2] / "demo_data" / "logs"
    if not logs.exists():
        return
    demo = P(__file__).resolve().parents[2] / "scripts" / "trade_analysis_demo.py"
    monkeypatch.setenv("TRADE_PARSER_SCRIPT", str(demo))
    created = TestClient(create_app()).post(
        "/api/runs",
        json={"domain": "trade", "sourcePath": "/backend/demo_data/logs/"},
    )
    assert created.status_code == 201


def test_create_run_from_folder(client: TestClient, tmp_path: Path):
    folder = tmp_path / "logs"
    folder.mkdir()
    _write_demo(folder)
    created = client.post("/api/runs", json={"domain": "trade", "sourcePath": str(folder)})
    assert created.status_code == 201
    assert created.json()["domain"] == "trade"


def test_validation_and_notification_not_configured(client: TestClient, tmp_path: Path):
    bad = client.post("/api/runs", json={"domain": "trade", "sourcePath": str(tmp_path / "nope")})
    assert bad.status_code == 400
    note = client.post("/api/runs", json={"domain": "notification", "sourcePath": str(tmp_path)})
    assert note.status_code == 501
    missing = client.get("/api/runs/latest/events/no-such")
    assert missing.status_code == 404


def test_latest_missing_before_run(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("STORE_DIR", str(tmp_path / "empty-store"))
    monkeypatch.setenv("SAMPLE_SOURCE_DIR", str(tmp_path / "empty-store"))
    fresh = TestClient(create_app())
    assert fresh.get("/api/runs/latest").status_code == 404
