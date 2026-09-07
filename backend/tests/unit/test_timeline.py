from pathlib import Path

from app.core.timeline import extract_exchange, extract_timeline

LOG = """\
[2026-06-03 15:24:56,422 Kafka-1][786712011][SL_ALTER_TRADE] LDTLINFO com.barclays.ldtl.trading.kafka.KafkaTradingSLTAgencyRequestConsumer - consumed AlterSLTradeRequest
[2026-06-03 15:24:56,422 EMT-LDS-Thread1][786712011][SL_ALTER_TRADE] LDTLDEBUG com.barclays.ldtl.trading.service.EMTService - sendEMTMessage() EMT Request Message: {"eventId":"ALTER_TRADE_786712011_1780496696422"}
[2026-06-03 15:24:56,423 SLT-4-C-1][786712011][SL_ALTER_TRADE] LDTLINFO com.barclays.ldtl.trading.util.JaxWsLoggingHandler - REQUEST MESSAGE
[2026-06-03 15:24:57,017 SLT-4-C-1][786712011][SL_ALTER_TRADE] LDTLINFO com.barclays.ldtl.trading.service.SecondaryLoanTradeProcessorService - ValidateMultipleFacilities isMigrated: false
[2026-06-03 15:24:57,100 EMT-LDS-Thread1][786712011][SL_ALTER_TRADE] LDTLINFO com.barclays.ldtl.trading.service.EMTService - EMT Response Message: Sent
[2026-06-03 15:24:57,200 SLT-4-C-1][999999][SL_CREATE_TRADE] LDTLINFO other - ignore
"""


def test_extracts_only_matching_trade_and_orders_hops(tmp_path: Path):
    log = tmp_path / "ldtl-trading-2026-06-03.1.log"
    log.write_text(LOG, encoding="utf-8")
    hops = extract_timeline("786712011", [str(log)])
    assert len(hops) == 5
    assert hops[0].service.endswith("KafkaTradingSLTAgencyRequestConsumer")
    assert hops[1].payload and "ALTER_TRADE_786712011" in hops[1].payload
    assert hops[3].gap_seconds == 0.594
    assert all(h.workflow == "SL_ALTER_TRADE" for h in hops)


def test_skips_missing_files_and_other_ids(tmp_path: Path):
    hops = extract_timeline("786712011", [str(tmp_path / "nope.log")])
    assert hops == []


def test_attaches_wrapped_lines_to_the_previous_hop(tmp_path: Path):
    log = tmp_path / "wrap.log"
    log.write_text(
        "[2026-08-24 13:04:56,423 SLT-1][786712011][SL_ALTER_TRADE] LDTLINFO "
        "com.ldtl.trading.util.JaxWsLoggingHandler - REQUEST MESSAGE\n"
        '<?xml version="1.0"?><AlterTradeRequest><settlementTradeId>786712011'
        "</settlementTradeId></AlterTradeRequest>\n"
        "[2026-08-24 13:04:57,000 SLT-1][999999][SL_CREATE_TRADE] LDTLINFO other - ignore\n",
        encoding="utf-8",
    )
    hops = extract_timeline("786712011", [str(log)])
    assert len(hops) == 1
    assert len(hops[0].lines) == 2
    assert hops[0].payload and "<AlterTradeRequest>" in hops[0].payload


def test_extract_exchange_unescapes_slt_payload_and_reads_success(tmp_path: Path):
    log = tmp_path / "exchange.log"
    inner = '{"messages":{"message":["ok"]},"success":"true","esettlementTradeId":"800615001"}'
    escaped = inner.replace('"', '\\"')
    log.write_text(
        "[2026-08-24 13:04:47,982 EMT-1][786712011][SL_ALTER_TRADE] LDTLDEBUG "
        "com.ldtl.trading.service.EMTService - sendEMTMessage() EMT Request Message: "
        '{"eventId":"ALTER_TRADE_786712011_1","payload":"' + escaped + '"}\n'
        "[2026-08-24 13:06:04,558 EMT-1][786712011][SL_ALTER_TRADE] LDTLINFO "
        "com.ldtl.trading.service.EMTService - Sending message "
        '{"messages":{"message":["Portfolio allocations have been updated."]},'
        '"success":"true","esettlementTradeId":"786712011"}\n',
        encoding="utf-8",
    )
    hops = extract_timeline("786712011", [str(log)])
    request, response, outcome = extract_exchange(hops)
    assert request and "800615001" in request
    assert "success" in request
    assert response and "Portfolio allocations have been updated." in response
    assert outcome == "SUCCESS"


def test_extract_exchange_maps_false_success_to_fail(tmp_path: Path):
    log = tmp_path / "fail.log"
    log.write_text(
        "[2026-08-24 13:21:00,000 EMT-1][999000][SL_ALTER_TRADE] LDTLINFO "
        "com.ldtl.trading.service.EMTService - Sending message "
        '{"messages":{"message":["rejected"]},"success":"false"}\n',
        encoding="utf-8",
    )
    hops = extract_timeline("999000", [str(log)])
    _request, response, outcome = extract_exchange(hops)
    assert response and "rejected" in response
    assert outcome == "FAIL"


def test_extract_exchange_reads_agency_create_trade_request(tmp_path: Path):
    log = tmp_path / "agency.log"
    log.write_text(
        "[2026-08-24 05:02:33,810 AGENCY-1][2900117][AGY_TRADE] LDTLINFO "
        "com.ldtl.trading.service.SecondaryLoanTradeProcessorService - "
        'Create trade request message received from LCX topic: request -> '
        '{"settlementTradeId":"2900117","dealInternalId":"WNGH58WU"}\n',
        encoding="utf-8",
    )
    hops = extract_timeline("2900117", [str(log)])
    request, _response, _outcome = extract_exchange(hops)
    assert request and "2900117" in request
    assert "WNGH58WU" in request
