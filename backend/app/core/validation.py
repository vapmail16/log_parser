from __future__ import annotations

from pathlib import Path

from app.core.errors import ValidationAppError


def _rooted_candidates(raw: str, search_roots: list[Path]) -> list[Path]:
    relative = Path(raw.strip().lstrip("/"))
    options: list[Path] = []
    seen: set[str] = set()
    for root in search_roots:
        for option in (root / relative,):
            try:
                resolved = option.resolve()
            except OSError:
                continue
            key = str(resolved)
            if key in seen:
                continue
            seen.add(key)
            options.append(resolved)
    return options


def validate_source_path(raw: str, search_roots: list[Path] | None = None) -> Path:
    if not raw or not str(raw).strip():
        raise ValidationAppError("sourcePath is required")
    text = raw.strip()
    roots = [Path(root) for root in (search_roots or [])]
    given = Path(text).expanduser()
    if given.is_absolute():
        resolved = given.resolve()
        if resolved.is_dir():
            return resolved
        if resolved.is_file():
            raise ValidationAppError("sourcePath must be a directory")
        for candidate in _rooted_candidates(text, roots):
            if candidate.is_dir():
                return candidate
    else:
        for candidate in _rooted_candidates(text, roots):
            if candidate.is_dir():
                return candidate
        cwd_relative = given.resolve()
        if cwd_relative.is_dir():
            return cwd_relative
        if cwd_relative.is_file():
            raise ValidationAppError("sourcePath must be a directory")
    raise ValidationAppError(
        "sourcePath does not exist. Use a full folder path on this machine "
        "(for sample logs use Load sample data, or the demo_data folder — not /backend/...)."
    )
