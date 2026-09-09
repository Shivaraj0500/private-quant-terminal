from datetime import datetime, timezone

import pytest

from private_quant_terminal.data.derivatives import (
    HistoricalOptionCandle,
    HistoricalOptionContract,
)
from private_quant_terminal.models.candle import Candle
from private_quant_terminal.models.instrument import (
    Instrument,
    InstrumentType,
    OptionType,
)


def option_instrument() -> Instrument:
    return Instrument(
        symbol="BANKNIFTY",
        exchange="NSE",
        instrument_type=InstrumentType.OPTION,
        expiry="2026-09-24",
        strike=55000.0,
        option_type=OptionType.CALL,
    )


def test_historical_option_contract_requires_concrete_option() -> None:
    contract = HistoricalOptionContract(
        instrument=option_instrument(),
        resolved_at=datetime(2026, 9, 9, 10, 0, tzinfo=timezone.utc),
    )

    assert contract.identifier == (
        "NSE:BANKNIFTY:OPTION:2026-09-24:55000.0:CE"
    )


def test_historical_option_contract_rejects_non_option() -> None:
    instrument = Instrument(
        symbol="BANKNIFTY",
        exchange="NSE",
        instrument_type=InstrumentType.INDEX,
    )

    with pytest.raises(ValueError, match="OPTION instrument"):
        HistoricalOptionContract(
            instrument=instrument,
            resolved_at=datetime(
                2026, 9, 9, 10, 0, tzinfo=timezone.utc
            ),
        )


def test_historical_option_contract_requires_timezone() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        HistoricalOptionContract(
            instrument=option_instrument(),
            resolved_at=datetime(2026, 9, 9, 10, 0),
        )


def test_historical_option_candle_delegates_ohlcv() -> None:
    contract = HistoricalOptionContract(
        instrument=option_instrument(),
        resolved_at=datetime(2026, 9, 9, 10, 0, tzinfo=timezone.utc),
    )

    candle = Candle(
        timestamp=datetime(2026, 9, 9, 10, 0, tzinfo=timezone.utc),
        open=100.0,
        high=110.0,
        low=95.0,
        close=105.0,
        volume=25.0,
    )

    historical = HistoricalOptionCandle(
        contract=contract,
        candle=candle,
    )

    assert historical.timestamp == candle.timestamp
    assert historical.open == 100.0
    assert historical.high == 110.0
    assert historical.low == 95.0
    assert historical.close == 105.0
    assert historical.volume == 25.0
