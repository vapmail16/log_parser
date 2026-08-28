from __future__ import annotations

import os
from pathlib import Path

LOCAL_PARSER_NAME = "trade_analysis_v2.py"
DEMO_SCRIPT_NAME = "trade_analysis_demo.py"


def backend_root() -> Path:
    return Path(__file__).resolve().parents[1]


def resolve_trade_parser_script(backend_dir: Path | None = None) -> Path | None:
    root = backend_dir or backend_root()
    scripts = root / "scripts"
    env = os.environ.get("TRADE_PARSER_SCRIPT", "").strip()
    if env:
        given = Path(env)
        candidates = [given]
        if not given.is_absolute():
            candidates.extend([Path.cwd() / given, scripts / given.name, root / given])
        for candidate in candidates:
            if candidate.is_file():
                return candidate.resolve()
    local_parser = scripts / LOCAL_PARSER_NAME
    if local_parser.is_file():
        return local_parser.resolve()
    demo = scripts / DEMO_SCRIPT_NAME
    if demo.is_file():
        return demo.resolve()
    return None


class Settings:
    def __init__(self) -> None:
        self.store_dir = Path(os.environ.get("STORE_DIR", backend_root() / "var" / "store"))
        self.sample_source_dir = Path(os.environ.get("SAMPLE_SOURCE_DIR", backend_root() / "demo_data" / "logs"))
        self.trade_parser_script = resolve_trade_parser_script()
        self.script_timeout_seconds = float(os.environ.get("TRADE_PARSER_TIMEOUT", "60"))
        self.search_roots = [Path.cwd(), backend_root(), backend_root().parent, self.sample_source_dir]
