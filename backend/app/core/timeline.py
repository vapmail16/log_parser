from __future__ import annotations

import gzip
import re
from datetime import datetime
from pathlib import Path

from app.core.models import Hop

LINE_PATTERN = re.compile(
    r"\[(?P<ts>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3})\s+(?P<thread>[^\]]+)\]"
    r"\[(?P<trade>[^\]]+)\]"
    r"\[(?P<workflow>[^\]]+)\]\s+"
    r"(?P<level>\S+)\s+"
    r"(?P<service>\S+)"
    r"(?:\s+-\s+(?P<summary>.*))?"
)


def _open_log(path: Path):
    if path.suffix == ".gz":
        return gzip.open(path, "rt", encoding="utf-8", errors="ignore")
    return path.open("rt", encoding="utf-8", errors="ignore")


def _parse_ts(raw: str) -> datetime:
    return datetime.strptime(raw, "%Y-%m-%d %H:%M:%S,%f")


def extract_timeline(trade_id: str, files: list[str]) -> list[Hop]:
    hops: list[Hop] = []
    for file_name in files:
        path = Path(file_name)
        if not path.exists() or not path.is_file():
            continue
        with _open_log(path) as handle:
            for line in handle:
                if trade_id not in line:
                    continue
                match = LINE_PATTERN.search(line)
                if not match:
                    continue
                rest = match.group("summary") or ""
                payload = rest if "{" in rest or "<" in rest or "success=" in rest else None
                hops.append(
                    Hop(
                        timestamp=_parse_ts(match.group("ts")),
                        thread=match.group("thread"),
                        service=match.group("service"),
                        workflow=match.group("workflow"),
                        level=match.group("level"),
                        summary=rest.split(":", 1)[0][:180],
                        payload=payload,
                        source_file=str(path),
                        gap_seconds=None,
                    )
                )
    hops.sort(key=lambda hop: hop.timestamp or datetime.min)
    previous = None
    for hop in hops:
        if previous and hop.timestamp and previous.timestamp:
            hop.gap_seconds = round((hop.timestamp - previous.timestamp).total_seconds(), 3)
        previous = hop
    return hops
