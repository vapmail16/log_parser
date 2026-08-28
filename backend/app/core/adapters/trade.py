from __future__ import annotations

from pathlib import Path

from app.config import resolve_trade_parser_script
from app.core.adapters.base import LogDomainAdapter
from app.core.errors import ValidationAppError
from app.core.models import Event
from app.core.script_runner import run_parser_script
from app.core.xlsx_ingest import find_workbook, ingest_trade_workbook


class TradeAdapter:
    domain = "trade"

    def __init__(
        self,
        script_path: Path | None = None,
        timeout_seconds: float = 60,
        backend_dir: Path | None = None,
    ) -> None:
        self.script_path = script_path
        self.timeout_seconds = timeout_seconds
        self.backend_dir = backend_dir

    def parse(self, source: Path) -> list[Event]:
        script = self.script_path or resolve_trade_parser_script(self.backend_dir)
        if script is None or not script.is_file():
            raise ValidationAppError(
                "Parser script is not configured. Place trade_analysis_v2.py in backend/scripts "
                "or set TRADE_PARSER_SCRIPT."
            )
        run_parser_script(script, source, timeout_seconds=self.timeout_seconds)
        workbook = find_workbook(source)
        if workbook is None:
            raise ValidationAppError("Parser script finished but produced no output to read")
        return ingest_trade_workbook(workbook)


def as_adapter(script_path: Path | None) -> LogDomainAdapter:
    return TradeAdapter(script_path=script_path)
