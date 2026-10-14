from pathlib import Path

from parse_payments import (
    collect_log_files,
    extract_hits,
    load_config,
    summarize,
)

SAMPLE = """\
[2026-10-14 09:01:02,100 pay-1][WSL8715367767048][PAYMENT] INFO PaymentClient - sending payment {"paymentTransactionReference":"WSL8715367767048","amount":"10.00"}
[2026-10-14 09:01:04,250 pay-1][WSL8715367767048][PAYMENT] INFO PaymentClient - response received {"paymentTransactionReference":"WSL8715367767048","success":"true"}
[2026-10-14 09:10:00,000 pay-2][WSL111][PAYMENT] INFO PaymentClient - sending payment {"paymentTransactionReference":"WSL111"}
[2026-10-14 10:00:00,001 other][999][OTHER] INFO Other - ignore
"""

WRAP = """\
[2026-10-14 11:00:00,000 pay-3][WSL222][PAYMENT] INFO PaymentClient - sending payment
{"paymentTransactionReference":"WSL222","status":"NEW"}
[2026-10-14 11:00:05,500 pay-3][WSL222][PAYMENT] INFO PaymentClient - payment response
{"paymentTransactionReference":"WSL222","success":"true"}
"""


def test_extracts_reference_and_send_and_response_times():
    hits = extract_hits(SAMPLE.splitlines())
    rows = summarize(hits)
    wsl = next(row for row in rows if row["payment_transaction_reference"] == "WSL8715367767048")
    assert wsl["sent_at"] == "2026-10-14 09:01:02.100"
    assert wsl["response_at"] == "2026-10-14 09:01:04.250"
    assert wsl["duration_seconds"] == 2.15
    assert wsl["status"] == "Matched"


def test_unmatched_when_no_response_line():
    hits = extract_hits(SAMPLE.splitlines())
    rows = summarize(hits)
    wsl = next(row for row in rows if row["payment_transaction_reference"] == "WSL111")
    assert wsl["sent_at"] == "2026-10-14 09:10:00.000"
    assert wsl["response_at"] is None
    assert wsl["status"] == "Unmatched"


def test_attaches_wrapped_json_to_previous_timestamp():
    hits = extract_hits(WRAP.splitlines())
    rows = summarize(hits)
    wsl = next(row for row in rows if row["payment_transaction_reference"] == "WSL222")
    assert wsl["sent_at"] == "2026-10-14 11:00:00.000"
    assert wsl["response_at"] == "2026-10-14 11:00:05.500"
    assert wsl["status"] == "Matched"


def test_reads_folder_of_plain_and_gz_logs(tmp_path: Path):
    folder = tmp_path / "logs"
    folder.mkdir()
    (folder / "a.log").write_text(SAMPLE, encoding="utf-8")
    import gzip

    with gzip.open(folder / "b.log.gz", "wt", encoding="utf-8") as handle:
        handle.write(WRAP)
    files = collect_log_files(folder)
    assert len(files) == 2
    from parse_payments import parse_folder

    rows = parse_folder(folder)
    refs = {row["payment_transaction_reference"] for row in rows}
    assert refs == {"WSL8715367767048", "WSL111", "WSL222"}


def test_writes_excel_workbook(tmp_path: Path):
    from parse_payments import write_workbook

    rows = [
        {
            "payment_transaction_reference": "WSL8715367767048",
            "sent_at": "2026-10-14 09:01:02.100",
            "response_at": "2026-10-14 09:01:04.250",
            "duration_seconds": 2.15,
            "status": "Matched",
            "source_files": "a.log",
        }
    ]
    path = tmp_path / "payment_timings.xlsx"
    write_workbook(rows, path)
    from openpyxl import load_workbook

    sheet = load_workbook(path).active
    headers = [cell.value for cell in sheet[1]]
    assert headers == [
        "Payment Transaction Reference",
        "Sent At",
        "Response At",
        "Duration Seconds",
        "Status",
        "Source Files",
    ]
    assert sheet[2][0].value == "WSL8715367767048"
    assert sheet[2][4].value == "Matched"


def test_load_config_reads_log_folder(tmp_path: Path):
    logs = tmp_path / "paylogs"
    logs.mkdir()
    config = tmp_path / "config.json"
    config.write_text('{"log_folder": "' + str(logs).replace("\\", "/") + '"}\n', encoding="utf-8")
    loaded = load_config(config)
    assert loaded == logs.resolve()
