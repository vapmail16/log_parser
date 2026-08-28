from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.core.models import Event, Hop, Run


@pytest.fixture
def tmp_store_dir(tmp_path: Path) -> Path:
    return tmp_path / "store"


def make_event(**overrides) -> Event:
    base = dict(
        id="trade:SLT:SL_ALTER_TRADE:786712011",
        domain="trade",
        display_id="786712011",
        group_id="HH0Y9V9",
        category="SLT",
        workflow="SL_ALTER_TRADE",
        request_type="SLT Trade Settlement",
        status="Matched",
        outcome="SUCCESS",
        start=datetime(2026, 8, 24, 13, 4, 47, 982000),
        end=datetime(2026, 8, 24, 13, 6, 4, 558000),
        duration_seconds=76.576,
        request_count=1,
        response_count=1,
        request_files=["ldtl-trading-2026-08-24.0.log"],
        response_files=["ldtl-trading-2026-08-24.0.log"],
        request_payload="<request/>",
        response_payload='success="true"',
        tags={},
    )
    base.update(overrides)
    return Event(**base)


@pytest.fixture
def sample_events() -> list[Event]:
    return [
        make_event(),
        make_event(
            id="trade:SLT:SL_CREATE_SUB_ALLOCATION:821933",
            display_id="821933",
            group_id="2RHGFARI",
            workflow="SL_CREATE_SUB_ALLOCATION",
            request_type="SLT Trade Allocation",
            start=datetime(2026, 8, 24, 7, 4, 47, 982000),
            end=datetime(2026, 8, 24, 7, 6, 4, 558000),
            duration_seconds=99.279,
            request_count=2,
        ),
        make_event(
            id="trade:Agency:AGY_TRADE:2900117",
            display_id="2900117",
            group_id="WNGH58WU",
            category="Agency",
            workflow="AGY_TRADE",
            request_type="Agency Trade",
            start=datetime(2026, 8, 24, 5, 2, 33, 748000),
            end=datetime(2026, 8, 24, 5, 2, 51, 86000),
            duration_seconds=17.338,
        ),
        make_event(
            id="trade:Agency:AGY_TRADE:2890940",
            display_id="2890940",
            group_id="UVGMWGKV",
            category="Agency",
            workflow="AGY_TRADE",
            request_type="Agency Trade",
            status="Unmatched",
            outcome=None,
            start=datetime(2026, 8, 24, 5, 10, 0),
            end=None,
            duration_seconds=None,
            response_count=0,
            response_files=[],
            response_payload=None,
        ),
        make_event(
            id="trade:SLT:SL_ALTER_TRADE:999000",
            display_id="999000",
            group_id="FAILDEAL",
            outcome="FAIL",
            start=datetime(2026, 8, 24, 13, 20, 0),
            end=datetime(2026, 8, 24, 13, 21, 0),
            duration_seconds=60.0,
            response_payload='success="false"',
        ),
    ]


@pytest.fixture
def sample_run(sample_events: list[Event]) -> Run:
    return Run(
        id="run-1",
        domain="trade",
        source_path="/logs",
        status="completed",
        events=sample_events,
    )


@pytest.fixture
def sample_hop() -> Hop:
    return Hop(
        timestamp=datetime(2026, 6, 3, 15, 24, 56, 422000),
        thread="EMT-LDS-Thread1",
        service="com.barclays.ldtl.trading.service.EMTService",
        workflow="SL_ALTER_TRADE",
        level="LDTLDEBUG",
        summary="sendEMTMessage() EMT Request Message",
        payload='{"eventId":"ALTER_TRADE_786712011_1"}',
        source_file="ldtl-trading-2026-06-03.1.log",
        gap_seconds=None,
    )
