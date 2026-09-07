from pathlib import Path

from app.core.sample_logs import SAMPLE_TRADES, file_for_trade, write_sample_logs
from app.core.timeline import extract_exchange, extract_timeline


def test_sample_logs_match_expected_shape_and_extract(tmp_path: Path):
    files = write_sample_logs(tmp_path / "logs")
    names = {path.name for path in files}
    assert "ldtl-trading-2026-08-24.0.log.gz" in names
    assert "ldtl-trading-2026-08-24.1.log" in names
    assert "ldtl-trading-2026-08-24.2.log.gz" in names

    paths = [str(path) for path in files]
    hops = extract_timeline("786712011", paths)
    services = " ".join(hop.service or "" for hop in hops)
    assert "KafkaTradingSLTAgencyRequestConsumer" in services
    assert "EMTService" in services
    assert "JaxWsLoggingHandler" in services
    assert "SecondaryLoanTradeProcessorService" in services
    text = " ".join((hop.payload or hop.summary) for hop in hops)
    assert "ALTER_TRADE_786712011" in text
    assert "LOANIQ" in text
    assert "REQUEST MESSAGE" in text
    assert "<?xml" in text
    assert "Response sent to LCX" in text
    request, response, outcome = extract_exchange(hops)
    assert request and "800615001" in request
    assert response and "Portfolio allocations have been updated." in response
    assert outcome == "SUCCESS"


def test_sample_logs_include_unmatched_fail_and_retry_trades(tmp_path: Path):
    files = write_sample_logs(tmp_path / "logs")
    paths = [str(path) for path in files]
    unmatched = extract_timeline("2890940", paths)
    assert unmatched
    assert not any("Response sent to LCX" in (hop.summary or "") for hop in unmatched)

    failed = extract_timeline("999000", paths)
    assert any(hop.payload and 'success="false"' in hop.payload for hop in failed)

    retry = extract_timeline("821933", paths)
    processing = [hop for hop in retry if "PROCESSING - Trade" in (hop.summary or "")]
    assert len(processing) >= 2

    assert file_for_trade(tmp_path / "logs", "786712011").name.endswith(".2.log.gz")
    assert {row["trade_id"] for row in SAMPLE_TRADES} >= {
        "786712011",
        "821933",
        "999000",
        "810006027",
        "2900117",
        "2890940",
    }
