from pathlib import Path

from app.config import resolve_trade_parser_script


def test_prefers_local_parser_over_demo(tmp_path: Path, monkeypatch: object) -> None:
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    local_parser = scripts / "trade_analysis_v2.py"
    local_parser.write_text("# local parser\n", encoding="utf-8")
    (scripts / "trade_analysis_demo.py").write_text("# demo\n", encoding="utf-8")
    monkeypatch.delenv("TRADE_PARSER_SCRIPT", raising=False)
    assert resolve_trade_parser_script(tmp_path) == local_parser.resolve()


def test_falls_back_to_demo_when_local_parser_is_absent(tmp_path: Path, monkeypatch: object) -> None:
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    demo = scripts / "trade_analysis_demo.py"
    demo.write_text("# demo\n", encoding="utf-8")
    monkeypatch.delenv("TRADE_PARSER_SCRIPT", raising=False)
    assert resolve_trade_parser_script(tmp_path) == demo.resolve()


def test_env_override_wins_when_that_file_exists(tmp_path: Path, monkeypatch: object) -> None:
    custom = tmp_path / "custom_parser.py"
    custom.write_text("# custom\n", encoding="utf-8")
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "trade_analysis_v2.py").write_text("# ignored\n", encoding="utf-8")
    monkeypatch.setenv("TRADE_PARSER_SCRIPT", str(custom))
    assert resolve_trade_parser_script(tmp_path) == custom.resolve()


def test_relative_env_name_resolves_inside_scripts(tmp_path: Path, monkeypatch: object) -> None:
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    target = scripts / "trade_analysis_v2.py"
    target.write_text("# v2\n", encoding="utf-8")
    monkeypatch.setenv("TRADE_PARSER_SCRIPT", "trade_analysis_v2.py")
    assert resolve_trade_parser_script(tmp_path) == target.resolve()


def test_returns_none_when_no_script_exists(tmp_path: Path, monkeypatch: object) -> None:
    monkeypatch.delenv("TRADE_PARSER_SCRIPT", raising=False)
    assert resolve_trade_parser_script(tmp_path) is None
