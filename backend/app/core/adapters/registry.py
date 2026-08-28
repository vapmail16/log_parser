from __future__ import annotations

from pathlib import Path

from app.core.adapters.base import LogDomainAdapter
from app.core.adapters.notification import NotificationAdapter
from app.core.adapters.trade import TradeAdapter
from app.core.errors import NotFoundError


class AdapterRegistry:
    def __init__(self, trade_script: Path | None = None, timeout_seconds: float = 60) -> None:
        self._adapters: dict[str, LogDomainAdapter] = {
            "trade": TradeAdapter(script_path=trade_script, timeout_seconds=timeout_seconds),
            "notification": NotificationAdapter(),
        }

    def get(self, domain: str) -> LogDomainAdapter:
        try:
            return self._adapters[domain]
        except KeyError as exc:
            raise NotFoundError(f"Unknown domain: {domain}") from exc

    def list_domains(self) -> list[dict[str, str]]:
        return [
            {
                "id": "trade",
                "label": "Trade processing",
                "status": "ready",
            },
            {
                "id": "notification",
                "label": "Notifications",
                "status": "not_configured",
            },
        ]
