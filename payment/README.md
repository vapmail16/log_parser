# Payment log timings

Parses a folder of payment logs and writes one Excel row per `paymentTransactionReference`.

Columns:

- **Sent At** — first send/request time for that reference
- **Response At** — later response time, or blank if none
- **Duration Seconds**
- **Status** — Matched or Unmatched
- **Source Files** — log file names that contained the reference

Send vs response is inferred from the log wording (`sending` / `request` vs `response` / `received` / `success`). If real logs use different markers, update `SEND_HINTS` and `RESPONSE_HINTS` in `parse_payments.py`.

## Setup

Python 3.10+ and `openpyxl` (same library as the trade parser):

```text
pip install openpyxl
```

1. Put `.log` and `.log.gz` files in a folder (subfolders are included).
2. Set the folder in `config.json`:

```json
{
  "log_folder": "C:\\path\\to\\payment\\logs"
}
```

A relative path is relative to this `payment` folder. Default `./sample_logs` is for a local dry run.

## Run

From this folder:

```text
python parse_payments.py
```

Or pass the folder (overrides config):

```text
python parse_payments.py "C:\path\to\payment\logs"
```

Output is `payment_timings.xlsx` in the log folder. Multiple files and multiple references in one file are supported; the same reference across files is still one row.

## What it looks for

```text
"paymentTransactionReference":"WSL8715367767048"
```

Timestamp from the log header:

```text
[2026-10-14 09:01:02,100 thread][id][WORKFLOW] ...
```

JSON that wraps onto the next line stays on that header.

## Tests

```text
python -m pytest tests -q
```
