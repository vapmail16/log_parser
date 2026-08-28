from __future__ import annotations

from pathlib import Path

from openpyxl import Workbook

from app.core.sample_logs import SAMPLE_TRADES

OUTPUT_NAME = "trade_analysis.xlsx"

SLT_ROWS = [
    ("SL_ALTER_TRADE", "SLT Trade Settlement", "786712011", "HH0Y9V9", "Matched", "2026-08-24 13:04:47.982", "2026-08-24 13:06:04.558", 76.576, 1, 1, "SUCCESS"),
    ("SL_CREATE_SUB_ALLOCATION", "SLT Trade Allocation", "821933", "2RHGFARI", "Matched", "2026-08-24 07:04:47.982", "2026-08-24 07:06:27.261", 99.279, 2, 1, "SUCCESS"),
    ("SL_ALTER_TRADE", "SLT Trade Settlement", "999000", "FAILDEAL", "Matched", "2026-08-24 13:20:00.000", "2026-08-24 13:21:00.000", 60.0, 1, 1, "FAIL"),
    ("SL_CREATE_TRADE", "SLT Trade Creation", "810006027", "2RHGFARI", "Matched", "2026-08-24 08:00:00.000", "2026-08-24 08:00:12.000", 12.0, 1, 1, "SUCCESS"),
]

AGENCY_ROWS = [
    ("2900117", "WNGH58WU", "Matched", "2026-08-24 05:02:33.748", "2026-08-24 05:02:51.086", 17.338, 1, 1, "SUCCESS"),
    ("2890940", "UVGMWGKV", "Unmatched", "2026-08-24 05:10:00.000", None, None, 1, 0, None),
]


def _file_for(folder: Path, trade_id: str) -> str:
    known = next((item["file"] for item in SAMPLE_TRADES if item["trade_id"] == trade_id), None)
    if known and (folder / known).exists():
        return str(folder / known)
    matches = sorted(folder.glob("ldtl-trading-*"))
    return str(matches[0]) if matches else ""


def write_parser_workbook(log_folder: Path) -> Path:
    output = log_folder / OUTPUT_NAME
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
    for row in SLT_ROWS:
        source = _file_for(log_folder, row[2])
        slt.append([*row[:8], row[8], row[9], source, source, "{}", 'success="true"' if row[10] == "SUCCESS" else 'success="false"', row[10]])
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
    for row in AGENCY_ROWS:
        source = _file_for(log_folder, row[0])
        agency.append([*row[:6], row[6], row[7], source, source if row[2] == "Matched" else "", "{}", 'success="true"' if row[8] == "SUCCESS" else "", row[8]])
    wb.save(output)
    return output
