from pathlib import Path

import pytest

from app.core.errors import ScriptRunnerError
from app.core.script_runner import run_parser_script


def test_runs_script_with_folder_argument(tmp_path: Path):
    script = tmp_path / "parser.py"
    marker = tmp_path / "ran.txt"
    script.write_text("import sys\nopen('ran.txt', 'w').write(sys.argv[1])\n")
    folder = tmp_path / "logs"
    folder.mkdir()
    run_parser_script(script, folder, timeout_seconds=5)
    assert (folder / "ran.txt").read_text() == str(folder)
    assert not marker.exists()


def test_timeout_and_nonzero_exit(tmp_path: Path):
    folder = tmp_path / "logs"
    folder.mkdir()
    sleeper = tmp_path / "sleep.py"
    sleeper.write_text("import time; time.sleep(5)\n")
    with pytest.raises(ScriptRunnerError):
        run_parser_script(sleeper, folder, timeout_seconds=0.2)
    fail = tmp_path / "fail.py"
    fail.write_text("raise SystemExit(2)\n")
    with pytest.raises(ScriptRunnerError):
        run_parser_script(fail, folder, timeout_seconds=5)
