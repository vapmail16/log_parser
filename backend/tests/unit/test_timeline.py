from pathlib import Path

from app.core.timeline import extract_timeline

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
