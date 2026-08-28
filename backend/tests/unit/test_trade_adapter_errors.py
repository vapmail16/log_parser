from pathlib import Path

import pytest

from app.core.adapters.trade import TradeAdapter
from app.core.errors import ValidationAppError


def test_trade_adapter_requires_script(tmp_path: Path):
    with pytest.raises(ValidationAppError, match="Parser script"):
        TradeAdapter(script_path=None, backend_dir=tmp_path).parse(tmp_path)


def test_trade_adapter_runs_dropped_local_parser(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    logs = tmp_path / "logs"
    logs.mkdir()
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    local_parser = scripts / "trade_analysis_v2.py"
    local_parser.write_text(
        "from pathlib import Path\n"
        "from openpyxl import Workbook\n"
        "import sys\n"
        "folder = Path(sys.argv[1])\n"
        "wb = Workbook()\n"
        "slt = wb.active\n"
        "slt.title = 'SLT'\n"
        "slt.append(['Workflow','Request Type','Trade ID','Deal ID','Status',"
        "'Processing Start','Response Time','Duration Seconds','Request Count',"
        "'Response Count','Request Source Files','Response Source Files',"
        "'Request Payload','Response Payload','Outcome'])\n"
        "slt.append(['SL_ALTER_TRADE','SLT Trade Settlement','111','DEAL','Matched',"
        "'2026-08-24 13:00:00','2026-08-24 13:00:10',10,1,1,'a.log','a.log','{}','','SUCCESS'])\n"
        "agency = wb.create_sheet('Agency')\n"
        "agency.append(['Trade ID','Deal ID','Status','Processing Start','Response Time',"
        "'Duration Seconds','Request Count','Response Count','Request Source Files',"
        "'Response Source Files','Request Payload','Response Payload','Outcome'])\n"
        "wb.save(folder / 'trade_analysis.xlsx')\n",
        encoding="utf-8",
    )
    monkeypatch.delenv("TRADE_PARSER_SCRIPT", raising=False)
    events = TradeAdapter(backend_dir=tmp_path).parse(logs)
    assert any(event.display_id == "111" for event in events)
