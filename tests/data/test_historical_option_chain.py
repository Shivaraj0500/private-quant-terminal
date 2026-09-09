from datetime import datetime, timezone

import pytest

from private_quant_terminal.data.derivatives.models import (
    HistoricalOptionChainSnapshot,
    HistoricalOptionContract,
    HistoricalOptionQuote,
)
from private_quant_terminal.models.instrument import (
    Instrument,
    InstrumentType,
    OptionType,
)


def option_contract(
    *,
    symbol: str = "BANKNIFTY",
    strike: float = 55000.0,
    option_type: OptionType = OptionType.CALL,
) -> HistoricalOptionContract:
    return HistoricalOptionContract(
        instrument=Instrument(
            symbol=symbol,
            exchange="NSE",
            instrument_type=InstrumentType.OPTION,
            expiry="2026-09-24",
            strike=strike,
            option_type=option_type,
        ),
        resolved_at=datetime(2026, 9, 9, 10, 0, tzinfo=timezone.utc),
    )


def quote(
    *,
    contract: HistoricalOptionContract | None = None,
    timestamp: datetime | None = None,
) -> HistoricalOptionQuote:
    return HistoricalOptionQuote(
        contract=contract or option_contract(),
        timestamp=timestamp
        or datetime(2026, 9, 9, 10, 0, tzinfo=timezone.utc),
        bid=100.0,
        ask=105.0,
        close=102.0,
    )


def test_quote_accepts_valid_point_in_time_data() -> None:
    result = quote()

    assert result.bid == 100.0
    assert result.ask == 105.0
    assert result.close == 102.0


def test_quote_rejects_crossed_market() -> None:
    with pytest.raises(ValueError, match="ask must be greater than or equal to bid"):
        HistoricalOptionQuote(
            contract=option_contract(),
            timestamp=datetime(2026, 9, 9, 10, 0, tzinfo=timezone.utc),
            bid=106.0,
            ask=105.0,
            close=105.5,
        )


def test_chain_normalizes_underlying() -> None:
    snapshot = HistoricalOptionChainSnapshot(
        timestamp=datetime(2026, 9, 9, 10, 0, tzinfo=timezone.utc),
        underlying=" banknifty ",
        underlying_price=55025.0,
        quotes=(quote(),),
    )

    assert snapshot.underlying == "BANKNIFTY"


def test_chain_accepts_matching_quotes() -> None:
    timestamp = datetime(2026, 9, 9, 10, 0, tzinfo=timezone.utc)

    snapshot = HistoricalOptionChainSnapshot(
        timestamp=timestamp,
        underlying="BANKNIFTY",
        underlying_price=55025.0,
        quotes=(
            quote(
                contract=option_contract(strike=55000.0),
                timestamp=timestamp,
            ),
            quote(
                contract=option_contract(
                    strike=55100.0,
                    option_type=OptionType.PUT,
                ),
                timestamp=timestamp,
            ),
        ),
    )

    assert len(snapshot.quotes) == 2


def test_chain_rejects_quote_for_different_underlying() -> None:
    with pytest.raises(
        ValueError,
        match="Option quote underlying does not match chain snapshot",
    ):
        HistoricalOptionChainSnapshot(
            timestamp=datetime(2026, 9, 9, 10, 0, tzinfo=timezone.utc),
            underlying="BANKNIFTY",
            underlying_price=55025.0,
            quotes=(quote(contract=option_contract(symbol="NIFTY")),),
        )


def test_chain_rejects_quote_at_different_timestamp() -> None:
    snapshot_timestamp = datetime(2026, 9, 9, 10, 0, tzinfo=timezone.utc)
    quote_timestamp = datetime(2026, 9, 9, 10, 1, tzinfo=timezone.utc)

    with pytest.raises(
        ValueError,
        match="Option quote timestamp must match chain snapshot timestamp",
    ):
        HistoricalOptionChainSnapshot(
            timestamp=snapshot_timestamp,
            underlying="BANKNIFTY",
            underlying_price=55025.0,
            quotes=(quote(timestamp=quote_timestamp),),
        )


def test_chain_rejects_non_positive_underlying_price() -> None:
    with pytest.raises(ValueError, match="underlying_price must be greater than zero"):
        HistoricalOptionChainSnapshot(
            timestamp=datetime(2026, 9, 9, 10, 0, tzinfo=timezone.utc),
            underlying="BANKNIFTY",
            underlying_price=0.0,
            quotes=(quote(),),
        )


def test_chain_rejects_naive_timestamp() -> None:
    with pytest.raises(ValueError, match="timestamp must be timezone-aware"):
        HistoricalOptionChainSnapshot(
            timestamp=datetime(2026, 9, 9, 10, 0),
            underlying="BANKNIFTY",
            underlying_price=55025.0,
            quotes=(
                quote(
                    timestamp=datetime(
                        2026, 9, 9, 10, 0, tzinfo=timezone.utc
                    )
                ),
            ),
        )


def test_chain_rejects_empty_underlying() -> None:
    with pytest.raises(ValueError, match="underlying must not be empty"):
        HistoricalOptionChainSnapshot(
            timestamp=datetime(2026, 9, 9, 10, 0, tzinfo=timezone.utc),
            underlying="   ",
            underlying_price=55025.0,
            quotes=(quote(),),
        )


def test_chain_accepts_multiple_option_quotes() -> None:
    timestamp = datetime(2026, 9, 9, 10, 0, tzinfo=timezone.utc)

    snapshot = HistoricalOptionChainSnapshot(
        timestamp=timestamp,
        underlying="BANKNIFTY",
        underlying_price=55025.0,
        quotes=(
            quote(
                contract=option_contract(
                    strike=55000.0,
                    option_type=OptionType.CALL,
                ),
                timestamp=timestamp,
            ),
            quote(
                contract=option_contract(
                    strike=55000.0,
                    option_type=OptionType.PUT,
                ),
                timestamp=timestamp,
            ),
        ),
    )

    assert len(snapshot.quotes) == 2


def chain_snapshot(
    *,
    timestamp: datetime,
    underlying: str = "BANKNIFTY",
    underlying_price: float = 55025.0,
) -> HistoricalOptionChainSnapshot:
    return HistoricalOptionChainSnapshot(
        timestamp=timestamp,
        underlying=underlying,
        underlying_price=underlying_price,
        quotes=(quote(timestamp=timestamp),),
    )


def test_provider_returns_latest_snapshot_at_or_before_as_of() -> None:
    from private_quant_terminal.data.derivatives import (
        InMemoryHistoricalOptionChainProvider,
    )

    first = datetime(2026, 9, 9, 10, 0, tzinfo=timezone.utc)
    second = datetime(2026, 9, 9, 10, 5, tzinfo=timezone.utc)
    as_of = datetime(2026, 9, 9, 10, 7, tzinfo=timezone.utc)

    provider = InMemoryHistoricalOptionChainProvider(
        snapshots=(
            chain_snapshot(timestamp=first),
            chain_snapshot(timestamp=second),
        )
    )

    result = provider.get_latest_chain("BANKNIFTY", as_of)

    assert result is not None
    assert result.timestamp == second


def test_provider_never_uses_future_snapshot() -> None:
    from private_quant_terminal.data.derivatives import (
        InMemoryHistoricalOptionChainProvider,
    )

    snapshot = datetime(2026, 9, 9, 10, 10, tzinfo=timezone.utc)
    as_of = datetime(2026, 9, 9, 10, 5, tzinfo=timezone.utc)

    provider = InMemoryHistoricalOptionChainProvider(
        snapshots=(chain_snapshot(timestamp=snapshot),)
    )

    assert provider.get_latest_chain("BANKNIFTY", as_of) is None


def test_provider_isolates_underlyings() -> None:
    from private_quant_terminal.data.derivatives import (
        InMemoryHistoricalOptionChainProvider,
    )

    timestamp = datetime(2026, 9, 9, 10, 0, tzinfo=timezone.utc)

    provider = InMemoryHistoricalOptionChainProvider(
        snapshots=(
            chain_snapshot(timestamp=timestamp, underlying="BANKNIFTY"),
        )
    )

    assert provider.get_latest_chain("NIFTY", timestamp) is None


def test_provider_accepts_normalized_underlying() -> None:
    from private_quant_terminal.data.derivatives import (
        InMemoryHistoricalOptionChainProvider,
    )

    timestamp = datetime(2026, 9, 9, 10, 0, tzinfo=timezone.utc)

    provider = InMemoryHistoricalOptionChainProvider(
        snapshots=(chain_snapshot(timestamp=timestamp),)
    )

    result = provider.get_latest_chain(" banknifty ", timestamp)

    assert result is not None
    assert result.underlying == "BANKNIFTY"


def test_provider_rejects_naive_as_of() -> None:
    from private_quant_terminal.data.derivatives import (
        InMemoryHistoricalOptionChainProvider,
    )

    provider = InMemoryHistoricalOptionChainProvider(snapshots=())

    with pytest.raises(ValueError, match="as_of must be timezone-aware"):
        provider.get_latest_chain(
            "BANKNIFTY",
            datetime(2026, 9, 9, 10, 0),
        )


def test_provider_rejects_empty_underlying() -> None:
    from private_quant_terminal.data.derivatives import (
        InMemoryHistoricalOptionChainProvider,
    )

    provider = InMemoryHistoricalOptionChainProvider(snapshots=())

    with pytest.raises(ValueError, match="underlying must not be empty"):
        provider.get_latest_chain(
            "   ",
            datetime(2026, 9, 9, 10, 0, tzinfo=timezone.utc),
        )
