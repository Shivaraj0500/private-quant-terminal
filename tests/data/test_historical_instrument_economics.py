from datetime import UTC, datetime

import pytest

from private_quant_terminal.data.economics import (
    HistoricalInstrumentEconomics,
    InMemoryHistoricalInstrumentEconomicsProvider,
    MarginRequirementType,
)
from private_quant_terminal.models.instrument import Instrument, InstrumentType

TIMESTAMP = datetime(2026, 9, 9, 10, 0, tzinfo=UTC)


def instrument(
    *,
    symbol: str = "NIFTY",
    instrument_type: InstrumentType = InstrumentType.FUTURE,
) -> Instrument:
    return Instrument(
        symbol=symbol,
        exchange="NSE",
        instrument_type=instrument_type,
        expiry="2026-09-24" if instrument_type is InstrumentType.FUTURE else None,
    )


def economics(
    *,
    timestamp: datetime = TIMESTAMP,
    instrument_value: Instrument | None = None,
    multiplier: float = 75.0,
    margin: float | None = 150000.0,
) -> HistoricalInstrumentEconomics:
    return HistoricalInstrumentEconomics(
        instrument=instrument_value or instrument(),
        timestamp=timestamp,
        contract_multiplier=multiplier,
        margin_requirement=margin,
        margin_requirement_type=(MarginRequirementType.ABSOLUTE if margin is not None else None),
    )


def test_accepts_valid_economics() -> None:
    result = economics()

    assert result.contract_multiplier == 75.0
    assert result.margin_requirement == 150000.0
    assert result.margin_requirement_type is MarginRequirementType.ABSOLUTE


def test_rejects_naive_timestamp() -> None:
    with pytest.raises(ValueError, match="timestamp must be timezone-aware"):
        economics(timestamp=datetime(2026, 9, 9, 10, 0))  # noqa: DTZ001


def test_rejects_non_positive_multiplier() -> None:
    with pytest.raises(
        ValueError,
        match="contract_multiplier must be greater than zero",
    ):
        economics(multiplier=0.0)


def test_requires_margin_type_when_margin_is_present() -> None:
    with pytest.raises(
        ValueError,
        match="margin_requirement_type is required",
    ):
        HistoricalInstrumentEconomics(
            instrument=instrument(),
            timestamp=TIMESTAMP,
            contract_multiplier=75.0,
            margin_requirement=150000.0,
        )


def test_rejects_margin_type_without_margin() -> None:
    with pytest.raises(
        ValueError,
        match="margin_requirement must be provided",
    ):
        HistoricalInstrumentEconomics(
            instrument=instrument(),
            timestamp=TIMESTAMP,
            contract_multiplier=75.0,
            margin_requirement_type=MarginRequirementType.ABSOLUTE,
        )


def test_provider_returns_latest_record_at_or_before_as_of() -> None:
    first = economics(timestamp=TIMESTAMP)
    second = economics(
        timestamp=datetime(2026, 9, 9, 10, 5, tzinfo=UTC),
        multiplier=80.0,
    )

    provider = InMemoryHistoricalInstrumentEconomicsProvider(records=(first, second))

    result = provider.get_latest_economics(
        instrument(),
        datetime(2026, 9, 9, 10, 7, tzinfo=UTC),
    )

    assert result is not None
    assert result.timestamp == second.timestamp
    assert result.contract_multiplier == 80.0


def test_provider_never_uses_future_record() -> None:
    provider = InMemoryHistoricalInstrumentEconomicsProvider(
        records=(economics(timestamp=datetime(2026, 9, 9, 10, 10, tzinfo=UTC)),)
    )

    assert (
        provider.get_latest_economics(
            instrument(),
            datetime(2026, 9, 9, 10, 5, tzinfo=UTC),
        )
        is None
    )


def test_provider_isolates_instruments() -> None:
    provider = InMemoryHistoricalInstrumentEconomicsProvider(records=(economics(),))

    assert (
        provider.get_latest_economics(
            instrument(symbol="BANKNIFTY"),
            TIMESTAMP,
        )
        is None
    )


def test_provider_rejects_naive_as_of() -> None:
    provider = InMemoryHistoricalInstrumentEconomicsProvider(records=())

    with pytest.raises(ValueError, match="as_of must be timezone-aware"):
        provider.get_latest_economics(
            instrument(),
            datetime(2026, 9, 9, 10, 0),  # noqa: DTZ001
        )


def test_provider_accepts_missing_margin_evidence() -> None:
    result = economics(margin=None)

    assert result.contract_multiplier == 75.0
    assert result.margin_requirement is None
    assert result.margin_requirement_type is None
