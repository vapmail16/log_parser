from pathlib import Path

import pytest

from app.core.errors import ValidationAppError
from app.core.validation import validate_source_path


def test_accepts_existing_directory(tmp_path: Path):
    assert validate_source_path(str(tmp_path)) == tmp_path.resolve()


def test_resolves_leading_slash_repo_relative_path(tmp_path: Path):
    target = tmp_path / "backend" / "demo_data" / "logs"
    target.mkdir(parents=True)
    found = validate_source_path("/backend/demo_data/logs/", search_roots=[tmp_path])
    assert found == target.resolve()


def test_resolves_relative_path_against_roots(tmp_path: Path):
    target = tmp_path / "demo_data" / "logs"
    target.mkdir(parents=True)
    found = validate_source_path("demo_data/logs", search_roots=[tmp_path])
    assert found == target.resolve()


def test_rejects_missing_and_file(tmp_path: Path):
    with pytest.raises(ValidationAppError, match="does not exist"):
        validate_source_path(str(tmp_path / "missing"))
    file_path = tmp_path / "a.log"
    file_path.write_text("x")
    with pytest.raises(ValidationAppError, match="must be a directory"):
        validate_source_path(str(file_path))


def test_rejects_empty():
    with pytest.raises(ValidationAppError):
        validate_source_path("  ")


def test_relative_file_is_rejected(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "notes.txt").write_text("x")
    with pytest.raises(ValidationAppError, match="must be a directory"):
        validate_source_path("notes.txt")
