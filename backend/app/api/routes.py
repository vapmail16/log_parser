from __future__ import annotations

import logging
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, Query, Request
from pydantic import BaseModel, Field

from app.api.serialize import event_to_public, filter_events, run_to_public, snapshot_for
from app.core.adapters.registry import AdapterRegistry
from app.core.errors import NotFoundError
from app.core.file_store import JsonFileStore
from app.core.models import Run
from app.core.store import RunStore
from app.core.timeline import extract_timeline
from app.config import LOCAL_PARSER_NAME, resolve_trade_parser_script
from app.core.validation import validate_source_path

logger = logging.getLogger("log_parser")


class RunRequest(BaseModel):
    domain: str = Field(min_length=1, max_length=64)
    source_path: str = Field(alias="sourcePath", min_length=1, max_length=1024)

    model_config = {"populate_by_name": True}


def get_store(request: Request) -> RunStore:
    return request.app.state.store


def get_registry(request: Request) -> AdapterRegistry:
    return request.app.state.registry


def get_sample_dir(request: Request) -> Path:
    return request.app.state.sample_source_dir


def get_search_roots(request: Request) -> list[Path]:
    return request.app.state.search_roots


def _latest(store: RunStore) -> Run:
    run = store.get_latest()
    if run is None:
        raise NotFoundError("No run yet. Analyze a log folder first.")
    return run


def build_router() -> APIRouter:
    router = APIRouter()

    @router.get("/health")
    def health(sample_dir: Path = Depends(get_sample_dir)) -> dict:
        script = resolve_trade_parser_script()
        return {
            "status": "ok",
            "samplePath": str(sample_dir),
            "parserScript": str(script) if script else None,
            "usingLocalParser": bool(script and script.name == LOCAL_PARSER_NAME),
        }

    @router.get("/domains")
    def domains(registry: AdapterRegistry = Depends(get_registry)) -> list[dict]:
        return registry.list_domains()

    @router.post("/runs", status_code=201)
    def create_run(
        payload: RunRequest,
        store: RunStore = Depends(get_store),
        registry: AdapterRegistry = Depends(get_registry),
        search_roots: list[Path] = Depends(get_search_roots),
    ) -> dict:
        source = validate_source_path(payload.source_path, search_roots=search_roots)
        adapter = registry.get(payload.domain)
        events = adapter.parse(source)
        run = Run(
            id=str(uuid.uuid4()),
            domain=payload.domain,
            source_path=str(source),
            status="completed",
            events=events,
        )
        store.save_run(run)
        logger.info("run_saved id=%s domain=%s events=%s", run.id, run.domain, len(events))
        return run_to_public(run)

    @router.post("/runs/sample", status_code=201)
    def create_sample_run(
        store: RunStore = Depends(get_store),
        registry: AdapterRegistry = Depends(get_registry),
        sample_dir: Path = Depends(get_sample_dir),
    ) -> dict:
        source = validate_source_path(str(sample_dir))
        events = registry.get("trade").parse(source)
        run = Run(
            id="sample",
            domain="trade",
            source_path=str(source),
            status="completed",
            events=events,
        )
        store.save_run(run)
        return run_to_public(run)

    @router.get("/runs/latest")
    def latest_run(store: RunStore = Depends(get_store)) -> dict:
        return run_to_public(_latest(store))

    @router.get("/runs/latest/metrics")
    def latest_metrics(
        category: str | None = Query(default=None),
        store: RunStore = Depends(get_store),
    ) -> dict:
        return snapshot_for(_latest(store), category)

    @router.get("/runs/latest/events")
    def latest_events(
        category: str | None = None,
        status: str | None = None,
        group_id: str | None = Query(default=None, alias="dealId"),
        hour: str | None = None,
        q: str | None = None,
        store: RunStore = Depends(get_store),
    ) -> dict:
        items = filter_events(
            _latest(store).events,
            category=category,
            status=status,
            group_id=group_id,
            hour=hour,
            q=q,
        )
        return {"items": [event_to_public(event) for event in items], "total": len(items)}

    @router.get("/runs/latest/events/{event_id}")
    def latest_event(event_id: str, store: RunStore = Depends(get_store)) -> dict:
        event = store.get_event(event_id)
        if event is None:
            raise NotFoundError("Event not found")
        return event_to_public(event)

    @router.get("/runs/latest/events/{event_id}/timeline")
    def latest_timeline(event_id: str, store: RunStore = Depends(get_store)) -> dict:
        event = store.get_event(event_id)
        if event is None:
            raise NotFoundError("Event not found")
        files = list(dict.fromkeys(event.request_files + event.response_files))
        hops = extract_timeline(event.display_id, files)
        return {"eventId": event.id, "hops": [hop.to_public() for hop in hops]}

    return router
