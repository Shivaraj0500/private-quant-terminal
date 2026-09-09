from datetime import datetime, timezone

import pytest

from private_quant_terminal.data.derivatives import (
    HistoricalOptionCandle,
    HistoricalOptionContract,
    HistoricalOptionCandleProvider,
    InMemoryHistoricalOptionCandleProvider,
)
from private_quant_terminal.models.candle import Candle
from private_quant_terminal.models.instrument import (
    Instrument,
    InstrumentType,
    OptionType,
)


UTC = timezone.utc


def make_contract(
    *,
    strike: float = 25000.0,
    option_type: OptionType = OptionType.CALL,
) -> HistoricalOptionContract:
    instrument = Instrument(
        symbol="BANKNIFTY",
        exchange="NSE",
        instrument_type=InstrumentType.OPTION,
        expiry="2026-09-24",
        strike=strike,
        option_type=option_type,
    )
    return HistoricalOptionContract(
        instrument=instrument,
        resolved_at=datetime(2026, 9, 9, 10, 0, tzinfo=UTC),
    )


def make_candle(
    contract: HistoricalOptionContract,
    timestamp: datetime,
    close: float,
) -> HistoricalOptionCandle:
    candle = Candle(
        timestamp=timestamp,
        open=close - 1.0,
        high=close + 2.0,
        low=close - 2.0,
        close=close,
        volume=100.0,
    )
    return HistoricalOptionCandle(
        contract=contract,
        candle=candle,
    )


def test_provider_is_runtime_protocol_compatible() -> None:
    contract = make_contract()
    provider = InMemoryHistoricalOptionCandleProvider(
        (
            make_candle(
                contract,
                datetime(2026, 9, 9, 10, 0, tzinfo=UTC),
                100.0,
            ),
        )
    )

    assert isinstance(provider, HistoricalOptionCandleProvider)


def test_returns_latest_candle_at_or_before_as_of() -> None:
    contract = make_contract()

    first = make_candle(
        contract,
        datetime(2026, 9, 9, 10, 0, tzinfo=UTC),
        100.0,
    )
    second = make_candle(
        contract,
        datetime(2026, 9, 9, 10, 5, tzinfo=UTC),
        110.0,
    )
    third = make_candle(
        contract,
        datetime(2026, 9, 9, 10, 10, tzinfo=UTC),
        120.0,
    )

    provider = InMemoryHistoricalOptionCandleProvider(
        (third, first, second)
    )

    result = provider.get_latest_candle(
        contract,
        datetime(2026, 9, 9, 10, 7, tzinfo=UTC),
    )

    assert result is second


def test_exact_timestamp_is_eligible() -> None:
    contract = make_contract()
    candle = make_candle(
        contract,
        datetime(2026, 9, 9, 10, 5, tzinfo=UTC),
        110.0,
    )

    provider = InMemoryHistoricalOptionCandleProvider((candle,))

    result = provider.get_latest_candle(
        contract,
        datetime(2026, 9, 9, 10, 5, tzinfo=UTC),
    )

    assert result is candle


def test_future_candle_is_never_returned() -> None:
    contract = make_contract()

    future = make_candle(
        contract,
        datetime(2026, 9, 9, 10, 10, tzinfo=UTC),
        120.0,
    )

    provider = InMemoryHistoricalOptionCandleProvider((future,))

    result = provider.get_latest_candle(
        contract,
        datetime(2026, 9, 9, 10, 5, tzinfo=UTC),
    )

    assert result is None


def test_returns_none_when_no_candle_exists_for_contract() -> None:
    contract = make_contract()
    other_contract = make_contract(strike=25100.0)

    candle = make_candle(
        other_contract,
        datetime(2026, 9, 9, 10, 0, tzinfo=UTC),
        100.0,
    )

    provider = InMemoryHistoricalOptionCandleProvider((candle,))

    result = provider.get_latest_candle(
        contract,
        datetime(2026, 9, 9, 10, 5, tzinfo=UTC),
    )

    assert result is None


def test_rejects_naive_as_of() -> None:
    contract = make_contract()

    provider = InMemoryHistoricalOptionCandleProvider(())

    with pytest.raises(ValueError, match="as_of must be timezone-aware"):
        provider.get_latest_candle(
            contract,
            datetime(2026, 9, 9, 10, 5),
        )
