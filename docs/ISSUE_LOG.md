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

## Local parser drop-in

- **What went wrong:** `trade_analysis_v2.py` in `backend/scripts` was ignored unless an env var was set.
- **Fix:** Resolve on each parse: env path, then `backend/scripts/trade_analysis_v2.py`, then the demo script.
