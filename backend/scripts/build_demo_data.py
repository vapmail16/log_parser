from __future__ import annotations

from pathlib import Path

from openpyxl import Workbook

from app.core.sample_logs import file_for_trade, write_sample_logs

ROOT = Path(__file__).resolve().parents[1] / "demo_data"
LOG_DIR = ROOT / "logs"


def _path(trade_id: str) -> str:
    return str(file_for_trade(LOG_DIR, trade_id))


def main() -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    stale = ROOT / "ldtl-trading-2026-08-24.0.log"
    if stale.exists():
        stale.unlink()
    write_sample_logs(LOG_DIR)

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
            _path("786712011"),
            _path("786712011"),
            '{"eventId":"ALTER_TRADE_786712011_1756040687982","sourceSystem":"LCX","destinationSystem":"LOANIQ"}',
            'success="true"',
            "SUCCESS",
        ]
    )
    slt.append(
        [
            "SL_CREATE_SUB_ALLOCATION",
            "SLT Trade Allocation",
            "821933",
            "2RHGFARI",
            "Matched",
            "2026-08-24 07:04:47.982",
            "2026-08-24 07:06:27.261",
            99.279,
            2,
            1,
            _path("821933"),
            _path("821933"),
            "{}",
            'success="true"',
            "SUCCESS",
        ]
    )
    slt.append(
        [
            "SL_ALTER_TRADE",
            "SLT Trade Settlement",
            "999000",
            "FAILDEAL",
            "Matched",
            "2026-08-24 13:20:00.000",
            "2026-08-24 13:21:00.000",
            60.0,
            1,
            1,
            _path("999000"),
            _path("999000"),
            "{}",
            'success="false"',
            "FAIL",
        ]
    )
    slt.append(
        [
            "SL_CREATE_TRADE",
            "SLT Trade Creation",
            "810006027",
            "2RHGFARI",
            "Matched",
            "2026-08-24 08:00:00.000",
            "2026-08-24 08:00:12.000",
            12.0,
            1,
            1,
            _path("810006027"),
            _path("810006027"),
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
            "2900117",
            "WNGH58WU",
            "Matched",
            "2026-08-24 05:02:33.748",
            "2026-08-24 05:02:51.086",
            17.338,
            1,
            1,
            _path("2900117"),
            _path("2900117"),
            "{}",
            'success="true"',
            "SUCCESS",
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
            _path("2890940"),
            "",
            "{}",
            "",
            None,
        ]
    )
    wb.save(ROOT / "trade_analysis.xlsx")


if __name__ == "__main__":
    main()
