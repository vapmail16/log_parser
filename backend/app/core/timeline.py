from __future__ import annotations

import gzip
import json
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


def _body(text: str) -> str | None:
    if "{" in text or "<" in text or "success=" in text:
        return text
    return None


def _append_line(hop: Hop, line: str) -> None:
    hop.lines.append(line)
    extra = _body(line)
    if extra:
        hop.payload = f"{hop.payload}\n{extra}" if hop.payload else extra


def extract_timeline(trade_id: str, files: list[str]) -> list[Hop]:
    hops: list[Hop] = []
    current: Hop | None = None
    for file_name in files:
        path = Path(file_name)
        if not path.exists() or not path.is_file():
            continue
        current = None
        with _open_log(path) as handle:
            for raw in handle:
                line = raw.rstrip("\n")
                match = LINE_PATTERN.search(line)
                if match:
                    if match.group("trade") != trade_id:
                        current = None
                        continue
                    rest = match.group("summary") or ""
                    current = Hop(
                        timestamp=_parse_ts(match.group("ts")),
                        thread=match.group("thread"),
                        service=match.group("service"),
                        workflow=match.group("workflow"),
                        level=match.group("level"),
                        summary=rest.split(":", 1)[0][:180],
                        payload=_body(rest),
                        source_file=str(path),
                        gap_seconds=None,
                        lines=[line],
                    )
                    hops.append(current)
                    continue
                if current is not None:
                    _append_line(current, line)
    hops.sort(key=lambda hop: hop.timestamp or datetime.min)
    previous = None
    for hop in hops:
        if previous and hop.timestamp and previous.timestamp:
            hop.gap_seconds = round((hop.timestamp - previous.timestamp).total_seconds(), 3)
        previous = hop
    return hops


def _brace_json(text: str, start_at: int = 0) -> str | None:
    start = text.find("{", start_at)
    if start < 0:
        return None
    depth = 0
    in_str = False
    escape = False
    for index, char in enumerate(text[start:], start):
        if in_str:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == '"':
                in_str = False
            continue
        if char == '"':
            in_str = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[start : index + 1]
    return None


def _unescape_payload(value: str) -> str:
    cleaned = value.replace("\\/", "/")
    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError:
        return cleaned.replace('\\"', '"')
    if isinstance(parsed, str):
        return parsed.replace("\\/", "/")
    return json.dumps(parsed, separators=(",", ":"))


def extract_exchange(hops: list[Hop]) -> tuple[str | None, str | None, str | None]:
    blob = "\n".join(line for hop in hops for line in (hop.lines or []))
    if not blob:
        blob = "\n".join(part for hop in hops for part in (hop.payload, hop.summary) if part)

    request: str | None = None
    agency_at = blob.find("Create trade request message received from LCX topic")
    if agency_at >= 0:
        request = _brace_json(blob, agency_at)

    emt_at = blob.find("EMT Request Message:")
    if emt_at >= 0:
        envelope = _brace_json(blob, emt_at)
        if envelope:
            try:
                data = json.loads(envelope)
            except json.JSONDecodeError:
                request = request or envelope
            else:
                inner = data.get("payload")
                if isinstance(inner, str) and inner.strip():
                    request = _unescape_payload(inner)
                elif request is None:
                    request = envelope

    response: str | None = None
    outcome: str | None = None
    send_at = blob.find("Sending message")
    if send_at >= 0:
        response = _brace_json(blob, send_at)
        if response:
            try:
                success = str(json.loads(response).get("success", "")).lower()
            except json.JSONDecodeError:
                success = "true" if '"success":"true"' in response else "false" if '"success":"false"' in response else ""
            if success == "true":
                outcome = "SUCCESS"
            elif success == "false":
                outcome = "FAIL"
    return request, response, outcome
