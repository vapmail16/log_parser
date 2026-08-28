from pathlib import Path

import pytest

from app.core.adapters.notification import NotificationAdapter
from app.core.adapters.registry import AdapterRegistry
from app.core.adapters.trade import TradeAdapter
from app.core.errors import DomainNotConfiguredError, NotFoundError
from app.core.demo_parser import OUTPUT_NAME
from app.core.sample_logs import write_sample_logs


def test_trade_adapter_runs_script_then_shows_events(tmp_path: Path):
    logs = tmp_path / "logs"
    write_sample_logs(logs)
    script = Path(__file__).resolve().parents[2] / "scripts" / "trade_analysis_demo.py"
    events = TradeAdapter(script_path=script).parse(logs)
    assert (logs / OUTPUT_NAME).exists()
    assert {event.display_id for event in events} >= {"786712011", "2890940"}


def test_registry_trade_and_notification_stub():
    registry = AdapterRegistry()
    assert registry.get("trade").domain == "trade"
    assert [d["id"] for d in registry.list_domains()] == ["trade", "notification"]
    with pytest.raises(DomainNotConfiguredError):
        registry.get("notification").parse(Path("."))
    with pytest.raises(NotFoundError):
        registry.get("unknown")
