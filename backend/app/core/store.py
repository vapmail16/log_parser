from __future__ import annotations

from typing import Protocol

from app.core.models import Event, Run


class RunStore(Protocol):
    def save_run(self, run: Run) -> None: ...

    def get_latest(self) -> Run | None: ...

    def get_event(self, event_id: str) -> Event | None: ...
