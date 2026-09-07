# Issue log

Engineering notes for this project. Append a row when something goes wrong.

## Parser must run on the log folder

- **What went wrong:** Analyze treated an existing xlsx as the input.
- **Fix:** Always run the parser script with cwd = log folder, then ingest its output.
- **Avoid:** Do not make spreadsheet ingest the happy path.

## Do not remap an existing `logs` directory

- **What went wrong:** Matching on basename `logs` rewrote a valid folder onto `demo_data/logs`.
- **Fix:** If the given path is an existing directory, use it. Only rewrite missing `/backend/...` paths against repo roots.
- **Avoid:** Never remap an existing absolute directory via the last path segment.

## Idle hours are not 0% match

- **What went wrong:** Empty hours looked like match-rate failures.
- **Fix:** `match_rate` is null when `started == 0`. Charts break the line on those hours.
- **Avoid:** Do not plot idle hours as 0%.

## Duration KPIs need more than the average

- **What went wrong:** Average hid slow outliers.
- **Fix:** KPIs include avg, p95, and max duration.

## Logging `extra={"message": ...}` crashes

- **What went wrong:** `message` is reserved on `LogRecord`.
- **Fix:** Use `detail` in `extra`.
- **Avoid:** Do not put reserved LogRecord fields in `extra`.

## SVG `transform` is not a settable DOM property

- **What went wrong:** Interpolating `transform="rotate(...)"` crashed detectChanges.
- **Fix:** Bind `[attr.transform]`.
- **Avoid:** Use `attr.*` for SVG attributes (`transform`, `d`, `viewBox`).

## Scripts that import `app` need PYTHONPATH

- **What went wrong:** `build_demo_data.py` failed with `No module named 'app'`.
- **Fix:** `PYTHONPATH=. .venv/bin/python scripts/build_demo_data.py` from `backend/`.

## Playwright must click a hop that has a payload

- **What went wrong:** The first timeline hop is often Kafka consume with no body.
- **Fix:** Click the EMT request hop when asserting payload text.

## Corporate npm may reject lockfile packages

- **What went wrong:** `npm ci` failed with registry 404 or 403 on `p-map@7.0.7` (Angular CLI transitive dep).
- **Fix:** Install from the default company registry, not npmjs. Override `p-map` to a version the registry has, or copy a complete `node_modules`.
- **Avoid:** Do not use `npm ci --registry https://registry.npmjs.org` on a locked-down network.

## Event hops can wrap onto the next log line

- **What went wrong:** Timeline kept only the header line, so XML/JSON bodies that wrap were dropped.
- **Fix:** Attach non-header lines to the previous hop until the next timestamped header.
- **Avoid:** Do not require the trade id on every wrapped payload line.

## Local parser drop-in

- **What went wrong:** `trade_analysis_v2.py` in `backend/scripts` was ignored unless an env var was set.
- **Fix:** Resolve on each parse: env path, then `backend/scripts/trade_analysis_v2.py`, then the demo script.

## Agency/SLT sheet omitted request and response JSON

- **What went wrong:** The parser writes Request Payload / Response Payload / Outcome, but the sheet UI only rendered Outcome. Event detail hid Request/Response when both were empty.
- **Fix:** Show those three fields on the Agency and SLT tables, and always show Request/Response blocks on event detail.
- **Avoid:** Do not treat event-detail-only JSON as meeting the workbook-column requirement.

## Windows log paths crush the Agency/SLT sheet

- **What went wrong:** `fileLabel` split only on `/`. Windows `C:\...\ldtl-trading-....log.gz` stayed one long cell, so Trade ID and other headers were squeezed off screen.
- **Fix:** Split on `/` and `\`. Cap file-column width.
- **Avoid:** Do not assume POSIX separators when showing parser source-file paths.

## Exchange hook goes after workflow, not at the request-message markers

- **What went wrong:** The extract_exchange call needs `workflow` and `trade_id`. Those are set after `WORKFLOW_PATTERN`, not at the `REQUEST MESSAGE` / `RESPONSE MESSAGE` `continue` block.
- **Fix:** Paste `extract_exchange_hook.py` after `workflow = workflow_match.group(1)` and the timestamp parse, still inside `for line in log_file:`.
- **Avoid:** Do not paste the hook before the workflow match; those earlier branches `continue` and never reach it.
