from __future__ import annotations

import gzip
from pathlib import Path

SAMPLE_TRADES = [
    {
        "trade_id": "786712011",
        "deal_id": "HH0Y9V9",
        "workflow": "SL_ALTER_TRADE",
        "file": "ldtl-trading-2026-08-24.2.log.gz",
    },
    {
        "trade_id": "821933",
        "deal_id": "2RHGFARI",
        "workflow": "SL_CREATE_SUB_ALLOCATION",
        "file": "ldtl-trading-2026-08-24.1.log",
    },
    {
        "trade_id": "999000",
        "deal_id": "FAILDEAL",
        "workflow": "SL_ALTER_TRADE",
        "file": "ldtl-trading-2026-08-24.2.log.gz",
    },
    {
        "trade_id": "810006027",
        "deal_id": "2RHGFARI",
        "workflow": "SL_CREATE_TRADE",
        "file": "ldtl-trading-2026-08-24.1.log",
    },
    {
        "trade_id": "2900117",
        "deal_id": "WNGH58WU",
        "workflow": "AGY_TRADE",
        "file": "ldtl-trading-2026-08-24.0.log.gz",
    },
    {
        "trade_id": "2890940",
        "deal_id": "UVGMWGKV",
        "workflow": "AGY_TRADE",
        "file": "ldtl-trading-2026-08-24.0.log.gz",
    },
]


def _line(ts: str, thread: str, trade_id: str, workflow: str, level: str, service: str, message: str) -> str:
    return f"[{ts} {thread}][{trade_id}][{workflow}] {level} {service} - {message}"


def _emt_json(event_id: str, message_type: str, trade_id: str, deal_id: str, extra: str = "") -> str:
    return (
        "{"
        f'"eventId":"{event_id}",'
        '"sourceSystem":"LCX",'
        '"destinationSystem":"LOANIQ",'
        f'"messageType":"{message_type}",'
        '"eventStatus":"payloadFinal",'
        f'"circleId":"{deal_id}",'
        f'"dealInternalId":"{deal_id}",'
        '"buySellCode":"SELL",'
        '"investmentType":"ASG",'
        '"tradeDate":"3/18/2026",'
        '"currency":"USD",'
        '"amount":"17053.44",'
        f'"settlementTradeId":"{trade_id}"'
        f"{extra}"
        "}"
    )


def _xml_request(trade_id: str, deal_id: str) -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="no"?>'
        f"<AlterTradeRequest><settlementTradeId>{trade_id}</settlementTradeId>"
        f"<FacilityPosition facilityInternalId=\"{deal_id}\" facilityCurrencyAmount=\"17053.44\" "
        'currency="USD" deleteIndicator="N"/></AlterTradeRequest>'
    )


def _xml_response(success: str) -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="no"?>'
        f'<AlterTradeResponse success="{success}"><buySellCode>SELL</buySellCode></AlterTradeResponse>'
    )


def _agency_lines() -> list[str]:
    return [
        _line(
            "2026-08-24 05:02:33,748",
            "AGENCY-1",
            "2900117",
            "AGY_TRADE",
            "LDTLINFO",
            "com.ldtl.trading.service.SecondaryLoanTradeProcessorService",
            "PROCESSING - Trade: 2900117, Deal: WNGH58WU",
        ),
        _line(
            "2026-08-24 05:02:33,810",
            "AGENCY-1",
            "2900117",
            "AGY_TRADE",
            "LDTLDEBUG",
            "com.ldtl.trading.kafka.KafkaTradingSLTAgencyRequestConsumer",
            "consumed AgencyTradeRequest",
        ),
        _line(
            "2026-08-24 05:02:40,100",
            "EMT-LDS-Thread1",
            "2900117",
            "AGY_TRADE",
            "LDTLDEBUG",
            "com.ldtl.trading.service.EMTService",
            "sendEMTMessage() EMT Request Message: "
            + _emt_json("AGY_TRADE_2900117_1756011753810", "AGY_TRADE", "2900117", "WNGH58WU"),
        ),
        _line(
            "2026-08-24 05:02:51,086",
            "AGENCY-1",
            "2900117",
            "AGY_TRADE",
            "LDTLINFO",
            "com.ldtl.trading.service.SecondaryLoanTradeProcessorService",
            'Response sent to LCX response topic for eSettlementTradeId: 2900117 success="true"',
        ),
        _line(
            "2026-08-24 05:10:00,012",
            "AGENCY-2",
            "2890940",
            "AGY_TRADE",
            "LDTLINFO",
            "com.ldtl.trading.service.SecondaryLoanTradeProcessorService",
            "PROCESSING - Trade: 2890940, Deal: UVGMWGKV",
        ),
        _line(
            "2026-08-24 05:10:00,140",
            "AGENCY-2",
            "2890940",
            "AGY_TRADE",
            "LDTLDEBUG",
            "com.ldtl.trading.kafka.KafkaTradingSLTAgencyRequestConsumer",
            "consumed AgencyTradeRequest",
        ),
        _line(
            "2026-08-24 05:10:01,200",
            "EMT-LDS-Thread2",
            "2890940",
            "AGY_TRADE",
            "LDTLDEBUG",
            "com.ldtl.trading.service.EMTService",
            "sendEMTMessage() EMT Request Message: "
            + _emt_json("AGY_TRADE_2890940_1756012200140", "AGY_TRADE", "2890940", "UVGMWGKV"),
        ),
    ]


def _morning_slt_lines() -> list[str]:
    first = [
        _line(
            "2026-08-24 07:04:47,982",
            "SLT-2-C-1",
            "821933",
            "SL_CREATE_SUB_ALLOCATION",
            "LDTLINFO",
            "com.ldtl.trading.service.SecondaryLoanTradeProcessorService",
            "PROCESSING - Trade: 821933, Deal: 2RHGFARI",
        ),
        _line(
            "2026-08-24 07:04:48,010",
            "Kafka-2",
            "821933",
            "SL_CREATE_SUB_ALLOCATION",
            "LDTLINFO",
            "com.ldtl.trading.kafka.KafkaTradingSLTAgencyRequestConsumer",
            "consumed CreateSubAllocationRequest",
        ),
        _line(
            "2026-08-24 07:05:10,400",
            "EMT-LDS-Thread1",
            "821933",
            "SL_CREATE_SUB_ALLOCATION",
            "LDTLDEBUG",
            "com.ldtl.trading.service.EMTService",
            "sendEMTMessage() EMT Request Message: "
            + _emt_json("ALLOC_821933_1756019088010", "SL_CREATE_SUB_ALLOCATION", "821933", "2RHGFARI"),
        ),
        _line(
            "2026-08-24 07:05:12,010",
            "SLT-2-C-1",
            "821933",
            "SL_CREATE_SUB_ALLOCATION",
            "LDTLINFO",
            "com.ldtl.trading.util.JaxWsLoggingHandler",
            "REQUEST MESSAGE " + _xml_request("821933", "2RHGFARI"),
        ),
        _line(
            "2026-08-24 07:05:40,200",
            "SLT-2-C-1",
            "821933",
            "SL_CREATE_SUB_ALLOCATION",
            "LDTLINFO",
            "com.ldtl.trading.service.SecondaryLoanTradeProcessorService",
            "PROCESSING - Trade: 821933, Deal: 2RHGFARI retry after timeout",
        ),
        _line(
            "2026-08-24 07:06:27,261",
            "SLT-2-C-1",
            "821933",
            "SL_CREATE_SUB_ALLOCATION",
            "LDTLINFO",
            "com.ldtl.trading.service.SecondaryLoanTradeProcessorService",
            'Response sent to LCX response topic for eSettlementTradeId: 821933 success="true"',
        ),
    ]
    create = [
        _line(
            "2026-08-24 08:00:00,000",
            "SLT-3-C-1",
            "810006027",
            "SL_CREATE_TRADE",
            "LDTLINFO",
            "com.ldtl.trading.service.SecondaryLoanTradeProcessorService",
            "PROCESSING - Trade: 810006027, Deal: 2RHGFARI",
        ),
        _line(
            "2026-08-24 08:00:00,080",
            "Kafka-3",
            "810006027",
            "SL_CREATE_TRADE",
            "LDTLINFO",
            "com.ldtl.trading.kafka.KafkaTradingSLTAgencyRequestConsumer",
            "consumed CreateSLTradeRequest",
        ),
        _line(
            "2026-08-24 08:00:04,200",
            "EMT-LDS-Thread3",
            "810006027",
            "SL_CREATE_TRADE",
            "LDTLDEBUG",
            "com.ldtl.trading.service.EMTService",
            "sendEMTMessage() EMT Request Message: "
            + _emt_json("CREATE_TRADE_810006027_1756022400080", "SL_CREATE_TRADE", "810006027", "2RHGFARI"),
        ),
        _line(
            "2026-08-24 08:00:12,000",
            "SLT-3-C-1",
            "810006027",
            "SL_CREATE_TRADE",
            "LDTLINFO",
            "com.ldtl.trading.service.SecondaryLoanTradeProcessorService",
            'Response sent to LCX response topic for eSettlementTradeId: 810006027 success="true"',
        ),
    ]
    return first + create


def _afternoon_slt_lines() -> list[str]:
    alter = [
        _line(
            "2026-08-24 13:04:47,982",
            "SLT-4-C-1",
            "786712011",
            "SL_ALTER_TRADE",
            "LDTLINFO",
            "com.ldtl.trading.service.SecondaryLoanTradeProcessorService",
            "PROCESSING - Trade: 786712011, Deal: HH0Y9V9",
        ),
        _line(
            "2026-08-24 13:04:47,982",
            "Kafka-1",
            "786712011",
            "SL_ALTER_TRADE",
            "LDTLINFO",
            "com.ldtl.trading.kafka.KafkaTradingSLTAgencyRequestConsumer",
            "consumed AlterSLTradeRequest",
        ),
        _line(
            "2026-08-24 13:04:47,982",
            "EMT-LDS-Thread1",
            "786712011",
            "SL_ALTER_TRADE",
            "LDTLDEBUG",
            "com.ldtl.trading.service.EMTService",
            "sendEMTMessage() EMT Request Message: "
            + _emt_json("ALTER_TRADE_786712011_1756040687982", "SL_ALTER_TRADE", "786712011", "HH0Y9V9"),
        ),
        _line(
            "2026-08-24 13:04:47,990",
            "SLT-4-C-1",
            "786712011",
            "SL_ALTER_TRADE",
            "LDTLINFO",
            "com.ldtl.trading.kafka.KafkaSender",
            "sending JSON "
            + _emt_json("ALTER_TRADE_786712011_1756040687982", "SL_ALTER_TRADE", "786712011", "HH0Y9V9"),
        ),
        _line(
            "2026-08-24 13:04:56,423",
            "SLT-4-C-1",
            "786712011",
            "SL_ALTER_TRADE",
            "LDTLINFO",
            "com.ldtl.trading.util.JaxWsLoggingHandler",
            "REQUEST MESSAGE " + _xml_request("786712011", "HH0Y9V9"),
        ),
        _line(
            "2026-08-24 13:05:57,017",
            "SLT-4-C-1",
            "786712011",
            "SL_ALTER_TRADE",
            "LDTLINFO",
            "com.ldtl.trading.service.SecondaryLoanTradeProcessorService",
            "ValidateMultipleFacilities isMigrated: false hasPikWithZeroAmount: false hasNonPikWithAmount: true",
        ),
        _line(
            "2026-08-24 13:06:00,200",
            "SLT-4-C-1",
            "786712011",
            "SL_ALTER_TRADE",
            "LDTLINFO",
            "com.ldtl.trading.service.LiqApiService",
            "XQuery result <buySellCode>SELL</buySellCode>",
        ),
        _line(
            "2026-08-24 13:06:04,400",
            "SLT-4-C-1",
            "786712011",
            "SL_ALTER_TRADE",
            "LDTLINFO",
            "com.ldtl.trading.util.JaxWsLoggingHandler",
            "RESPONSE MESSAGE " + _xml_response("true"),
        ),
        _line(
            "2026-08-24 13:06:04,558",
            "EMT-LDS-Thread1",
            "786712011",
            "SL_ALTER_TRADE",
            "LDTLINFO",
            "com.ldtl.trading.service.EMTService",
            "EMT Response Message: Sent",
        ),
        _line(
            "2026-08-24 13:06:04,558",
            "SLT-4-C-1",
            "786712011",
            "SL_ALTER_TRADE",
            "LDTLINFO",
            "com.ldtl.trading.service.SecondaryLoanTradeProcessorService",
            "Response sent to LCX response topic for eSettlementTradeId: 786712011",
        ),
    ]
    failed = [
        _line(
            "2026-08-24 13:20:00,000",
            "SLT-4-C-2",
            "999000",
            "SL_ALTER_TRADE",
            "LDTLINFO",
            "com.ldtl.trading.service.SecondaryLoanTradeProcessorService",
            "PROCESSING - Trade: 999000, Deal: FAILDEAL",
        ),
        _line(
            "2026-08-24 13:20:00,040",
            "Kafka-1",
            "999000",
            "SL_ALTER_TRADE",
            "LDTLINFO",
            "com.ldtl.trading.kafka.KafkaTradingSLTAgencyRequestConsumer",
            "consumed AlterSLTradeRequest",
        ),
        _line(
            "2026-08-24 13:20:10,100",
            "EMT-LDS-Thread2",
            "999000",
            "SL_ALTER_TRADE",
            "LDTLDEBUG",
            "com.ldtl.trading.service.EMTService",
            "sendEMTMessage() EMT Request Message: "
            + _emt_json("ALTER_TRADE_999000_1756041600040", "SL_ALTER_TRADE", "999000", "FAILDEAL"),
        ),
        _line(
            "2026-08-24 13:20:40,000",
            "SLT-4-C-2",
            "999000",
            "SL_ALTER_TRADE",
            "LDTLINFO",
            "com.ldtl.trading.util.JaxWsLoggingHandler",
            "RESPONSE MESSAGE " + _xml_response("false"),
        ),
        _line(
            "2026-08-24 13:21:00,000",
            "SLT-4-C-2",
            "999000",
            "SL_ALTER_TRADE",
            "LDTLINFO",
            "com.ldtl.trading.service.SecondaryLoanTradeProcessorService",
            'Response sent to LCX response topic for eSettlementTradeId: 999000 success="false"',
        ),
    ]
    return alter + failed


def _write_text(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    body = "\n".join(lines) + "\n"
    if path.suffix == ".gz":
        with gzip.open(path, "wt", encoding="utf-8") as handle:
            handle.write(body)
    else:
        path.write_text(body, encoding="utf-8")


def write_sample_logs(directory: Path) -> list[Path]:
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    mapping = {
        "ldtl-trading-2026-08-24.0.log.gz": _agency_lines(),
        "ldtl-trading-2026-08-24.1.log": _morning_slt_lines(),
        "ldtl-trading-2026-08-24.2.log.gz": _afternoon_slt_lines(),
    }
    written: list[Path] = []
    for name, lines in mapping.items():
        path = directory / name
        _write_text(path, lines)
        written.append(path)
    return written


def file_for_trade(directory: Path, trade_id: str) -> Path:
    row = next(item for item in SAMPLE_TRADES if item["trade_id"] == trade_id)
    return directory / row["file"]
