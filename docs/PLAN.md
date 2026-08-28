# Log Parser Ops Console

## Purpose

A console for trade log analysis. Point it at a folder of `.log` / `.log.gz` files, run the parser, and inspect Agency / SLT metrics, trade rows, and event timelines.

The parser script (`trade_analysis_v2.py`) writes `trade_analysis.xlsx`. That is the script’s CLI output, not the application store. The API ingests it once per run into JSON (`current_run.json`). The UI never opens Excel.

## Architecture

```
Angular (frontend/)  →  FastAPI (backend/)  →  Adapter registry
                                              ├─ trade (run parser, ingest output, timeline)
                                              └─ notification (stub, 501 until configured)
                                              ↓
                                         RunStore (JSON file now, DB later)
```

- UI calls `/api/*` only.
- Metrics and lists are served from the last run, not by grepping every log file.
- Event drill-down searches only the source files on that row.
- The parser runs once per `POST /api/runs`.

## Parser resolution

On each run the API picks the first available script:

1. `TRADE_PARSER_SCRIPT` if that path exists
2. `backend/scripts/trade_analysis_v2.py` if present
3. `backend/scripts/trade_analysis_demo.py`

`trade_analysis_v2.py` is gitignored. Drop it into `backend/scripts` to use it.

## Screens

| Route | Content |
|---|---|
| Overview | KPIs, charts (throughput, duration, match rate, status), hourly table, request-type mix, per-deal |
| Agency / SLT | Parser workbook columns; Trade ID opens event detail |
| Events | Filtered list and hop timeline |

## Quality gates

1. TDD on new behaviour
2. Backend `pytest --cov=app --cov-fail-under=90`; frontend unit coverage ≥90% on `src/app`
3. 100% test pass (unit, integration, Playwright)
4. 0 TypeScript errors, 0 lint errors
5. Playwright covers Run parser → KPIs/charts → sheet → event timeline

## API

- `GET /api/health`
- `GET /api/domains`
- `POST /api/runs` `{ domain, sourcePath }`
- `POST /api/runs/sample`
- `GET /api/runs/latest`
- `GET /api/runs/latest/metrics?category=Agency|SLT`
- `GET /api/runs/latest/events?...`
- `GET /api/runs/latest/events/{eventId}`
- `GET /api/runs/latest/events/{eventId}/timeline`

## How to run tests

```bash
cd backend && python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest

cd frontend
npm ci
npm run lint
npx ng test --no-watch --code-coverage
npx ng build
npx playwright test
```

## Extending

- New log type: add `adapters/<name>.py`, register it. Same screens, labels from `/api/domains`.
- Database: implement `RunStore`; keep route handlers unchanged.
- Live refresh: a watcher can call the same `POST /api/runs`.
