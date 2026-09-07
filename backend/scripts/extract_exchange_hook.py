"""Paste this into parse_logs, not at the top of the file.

In trade_analysis_v2.py, find this line (your photo, around line 249):

    workflow = workflow_match.group(1)

Then scroll a few lines down to the timestamp try/except. Paste the block
below AFTER that try/except, still inside `for line in log_file:`.

Do not paste it next to REQUEST_MESSAGE / RESPONSE_MESSAGE (lines 235-242).
Those lines `continue` before workflow exists.

The first two lines get trade_id from [tradeId][WORKFLOW] so this also
runs on EMT Request Message and Sending message lines.
"""

# --- copy from here (keep this indent) ---
        ids = re.search(r"\]\[([^\]]+)\]\[" + re.escape(workflow) + r"\]", line)
        if ids:
            trade_id = ids.group(1)
            kind = "Agency" if workflow == "AGY_TRADE" else "SLT"
            req, resp, out = extract_exchange(line, kind=kind)
            if req and requests[workflow][trade_id]["payload"] is None:
                requests[workflow][trade_id]["payload"] = req
            if resp:
                if responses[workflow][trade_id]["payload"] is None:
                    responses[workflow][trade_id]["payload"] = resp
                if out and responses[workflow][trade_id]["outcome"] is None:
                    responses[workflow][trade_id]["outcome"] = out
# --- copy until here ---
