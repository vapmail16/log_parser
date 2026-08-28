from pathlib import Path

from app.core.demo_parser import OUTPUT_NAME, write_parser_workbook
from app.core.sample_logs import write_sample_logs
from app.core.xlsx_ingest import ingest_trade_workbook


def test_demo_parser_writes_workbook_from_log_folder(tmp_path: Path):
    logs = tmp_path / "logs"
    write_sample_logs(logs)
    output = write_parser_workbook(logs)
    assert output.name == OUTPUT_NAME
    events = ingest_trade_workbook(output)
    assert any(event.display_id == "786712011" for event in events)
    assert any(event.status == "Unmatched" for event in events)
