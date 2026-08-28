from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from app.core.errors import ScriptRunnerError


def run_parser_script(script_path: Path, log_folder: Path, timeout_seconds: float = 60) -> None:
    command = [sys.executable, str(script_path), str(log_folder)]
    try:
        completed = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            cwd=str(log_folder),
        )
    except subprocess.TimeoutExpired as exc:
        raise ScriptRunnerError(f"Parser script timed out after {timeout_seconds}s") from exc
    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout or "").strip()[:400]
        raise ScriptRunnerError(f"Parser script failed: {detail or completed.returncode}")
