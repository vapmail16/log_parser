"""Copy these helpers into trade_analysis_v2.py.

When you already have the joined log text for one trade, call:

    request, response, outcome = extract_exchange(blob, kind="SLT")  # or "Agency"

Then write Request Payload, Response Payload, and Outcome on that row.
"""

import json


def _brace_json(text, start_at=0):
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


def _unescape_payload(value):
    cleaned = value.replace("\\/", "/")
    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError:
        return cleaned.replace('\\"', '"')
    if isinstance(parsed, str):
        return parsed.replace("\\/", "/")
    return json.dumps(parsed, separators=(",", ":"))


def extract_exchange(blob, kind="SLT"):
    request = None
    if kind == "Agency":
        at = blob.find("Create trade request message received from LCX topic")
        if at >= 0:
            request = _brace_json(blob, at)
    else:
        at = blob.find("EMT Request Message:")
        if at >= 0:
            envelope = _brace_json(blob, at)
            if envelope:
                try:
                    data = json.loads(envelope)
                    inner = data.get("payload")
                    request = _unescape_payload(inner) if isinstance(inner, str) and inner.strip() else envelope
                except json.JSONDecodeError:
                    request = envelope

    response = None
    outcome = None
    send_at = blob.find("Sending message")
    if send_at >= 0:
        response = _brace_json(blob, send_at)
        if response:
            try:
                success = str(json.loads(response).get("success", "")).lower()
            except json.JSONDecodeError:
                if '"success":"true"' in response:
                    success = "true"
                elif '"success":"false"' in response:
                    success = "false"
                else:
                    success = ""
            if success == "true":
                outcome = "SUCCESS"
            elif success == "false":
                outcome = "FAIL"
    return request, response, outcome
