from __future__ import annotations

from pathlib import Path
from typing import Protocol

from app.core.models import Event


class LogDomainAdapter(Protocol):
    domain: str

    def parse(self, source: Path) -> list[Event]: ...
