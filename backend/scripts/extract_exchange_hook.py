"""Replace the one-line hook in parse_logs with this.

1. Just after payload_lines = [] (inside with open_log_file):

        trade_lines = defaultdict(list)

2. Replace the current ids / extract_exchange(line) block with:

        ids = re.search(r"\]\[([^\]]+)\]\[" + re.escape(workflow) + r"\]", line)
        if ids:
            trade_lines[workflow][ids.group(1)].append(line)

3. At the end of that file, BEFORE statistics["files_processed"] += 1,
   after the leftover payload_text block:

        for wf, trades in trade_lines.items():
            kind = "Agency" if wf == "AGY_TRADE" else "SLT"
            for trade_id, lines in trades.items():
                req, resp, out = extract_exchange("\n".join(lines), kind=kind)
                if req and requests[wf][trade_id]["payload"] is None:
                    requests[wf][trade_id]["payload"] = req
                if resp:
                    if responses[wf][trade_id]["payload"] is None:
                        responses[wf][trade_id]["payload"] = resp
                    if out and responses[wf][trade_id]["outcome"] is None:
                        responses[wf][trade_id]["outcome"] = out
"""
