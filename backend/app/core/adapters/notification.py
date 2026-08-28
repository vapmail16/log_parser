from __future__ import annotations

from pathlib import Path

from app.core.errors import DomainNotConfiguredError
from app.core.models import Event


class NotificationAdapter:
    domain = "notification"

    def parse(self, source: Path) -> list[Event]:
        raise DomainNotConfiguredError(
            "Notification adapter is registered but not implemented. Add a parser later without changing the API."
        )
