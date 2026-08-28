from __future__ import annotations

import json
from pathlib import Path

from app.core.models import Event, Run
from app.core.store import RunStore


class JsonFileStore(RunStore):
    def __init__(self, directory: Path) -> None:
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        self._path = self.directory / "current_run.json"

    def save_run(self, run: Run) -> None:
        self._path.write_text(json.dumps(run.to_dict(), indent=2), encoding="utf-8")

    def get_latest(self) -> Run | None:
        if not self._path.exists():
            return None
        return Run.from_dict(json.loads(self._path.read_text(encoding="utf-8")))

    def get_event(self, event_id: str) -> Event | None:
        run = self.get_latest()
        if run is None:
            return None
        return next((event for event in run.events if event.id == event_id), None)
