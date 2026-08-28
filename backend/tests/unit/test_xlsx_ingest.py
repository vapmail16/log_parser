from datetime import datetime
from pathlib import Path

from openpyxl import Workbook

from app.core.xlsx_ingest import ingest_trade_workbook


def _write_workbook(path: Path) -> None:
    wb = Workbook()
    agency = wb.active
    agency.title = "Agency"
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
            "2900117",
            "WNGH58WU",
            "Matched",
            datetime(2026, 8, 24, 5, 2, 33, 748000),
            datetime(2026, 8, 24, 5, 2, 51, 86000),
            17.338,
            1,
            1,
            "a.log.gz",
            "a.log.gz",
            "{}",
            'success="true"',
            "SUCCESS",
        ]
    )
    slt = wb.create_sheet("SLT")
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
            "b.log.gz",
            "b.log.gz",
            "<xml/>",
            'success="true"',
            "SUCCESS",
        ]
    )
    wb.save(path)


def test_ingests_agency_and_slt_sheets(tmp_path: Path):
    xlsx = tmp_path / "trade_analysis.xlsx"
    _write_workbook(xlsx)
    events = ingest_trade_workbook(xlsx)
    assert {e.category for e in events} == {"Agency", "SLT"}
    slt = next(e for e in events if e.display_id == "786712011")
    assert slt.workflow == "SL_ALTER_TRADE"
    assert slt.duration_seconds == 76.576
    assert slt.request_files == ["b.log.gz"]
    agency = next(e for e in events if e.display_id == "2900117")
    assert agency.request_type == "Agency Trade"
