from datetime import datetime, timezone

import pytest

from private_quant_terminal.data.derivatives.models import (
    HistoricalOptionChainSnapshot,
    HistoricalOptionContract,
    HistoricalOptionQuote,
)
from private_quant_terminal.data.derivatives.resolver import (
    HistoricalOptionContractResolver,
)
from private_quant_terminal.models.instrument import (
    Instrument,
    InstrumentType,
    OptionType,
)
from private_quant_terminal.strategy.options import (
    ExpirySelection,
    OptionSelector,
    StrikeSelection,
)


UTC = timezone.utc


def make_quote(
    *,
    strike: float,
    option_type: OptionType,
    expiry: str = "2026-09-24",
    underlying: str = "BANKNIFTY",
    exchange: str = "NSE",
    timestamp: datetime = datetime(2026, 9, 9, 10, 0, tzinfo=UTC),
) -> HistoricalOptionQuote:
    contract = HistoricalOptionContract(
        instrument=Instrument(
            symbol=underlying,
            exchange=exchange,
            instrument_type=InstrumentType.OPTION,
            expiry=expiry,
            strike=strike,
            option_type=option_type,
        ),
        resolved_at=timestamp,
    )

    return HistoricalOptionQuote(
        contract=contract,
        timestamp=timestamp,
        bid=100.0,
        ask=105.0,
        close=102.0,
    )


def make_chain(
    *,
    underlying_price: float = 55025.0,
    quotes: tuple[HistoricalOptionQuote, ...],
    timestamp: datetime = datetime(2026, 9, 9, 10, 0, tzinfo=UTC),
) -> HistoricalOptionChainSnapshot:
    return HistoricalOptionChainSnapshot(
        timestamp=timestamp,
        underlying="BANKNIFTY",
        underlying_price=underlying_price,
        quotes=quotes,
    )


def selector(
    *,
    option_type: OptionType = OptionType.CALL,
    strike_selection: StrikeSelection = StrikeSelection.ATM,
    strike: float | None = None,
    expiry_selection: ExpirySelection = ExpirySelection.CURRENT_WEEK,
    expiry: str | None = None,
) -> OptionSelector:
    return OptionSelector(
        underlying="BANKNIFTY",
        option_type=option_type,
        strike_selection=strike_selection,
        strike=strike,
        expiry_selection=expiry_selection,
        expiry=expiry,
    )


def test_exact_strike_and_expiry_resolve_concrete_contract() -> None:
    timestamp = datetime(2026, 9, 9, 10, 0, tzinfo=UTC)
    chain = make_chain(
        quotes=(
            make_quote(
                strike=55000.0,
                option_type=OptionType.CALL,
                expiry="2026-09-24",
                timestamp=timestamp,
            ),
            make_quote(
                strike=55100.0,
                option_type=OptionType.CALL,
                expiry="2026-10-01",
                timestamp=timestamp,
            ),
        )
    )

    result = HistoricalOptionContractResolver().resolve(
        selector(
            option_type=OptionType.CALL,
            strike_selection=StrikeSelection.EXACT,
            strike=55100.0,
            expiry_selection=ExpirySelection.EXACT,
            expiry="2026-10-01",
        ),
        chain,
        as_of=timestamp,
    )

    assert result.instrument.symbol == "BANKNIFTY"
    assert result.instrument.exchange == "NSE"
    assert result.instrument.strike == 55100.0
    assert result.instrument.expiry == "2026-10-01"
    assert result.instrument.option_type is OptionType.CALL
    assert result.resolved_at == timestamp


def test_atm_selects_nearest_available_strike() -> None:
    timestamp = datetime(2026, 9, 9, 10, 0, tzinfo=UTC)
    chain = make_chain(
        underlying_price=55025.0,
        quotes=(
            make_quote(
                strike=54900.0,
                option_type=OptionType.CALL,
                timestamp=timestamp,
            ),
            make_quote(
                strike=55000.0,
                option_type=OptionType.CALL,
                timestamp=timestamp,
            ),
            make_quote(
                strike=55100.0,
                option_type=OptionType.CALL,
                timestamp=timestamp,
            ),
        ),
    )

    result = HistoricalOptionContractResolver().resolve(
        selector(),
        chain,
        as_of=timestamp,
    )

    assert result.instrument.strike == 55000.0


def test_itm_call_selects_lowest_strike_above_or_equal_to_boundary() -> None:
    timestamp = datetime(2026, 9, 9, 10, 0, tzinfo=UTC)
    chain = make_chain(
        underlying_price=55025.0,
        quotes=(
            make_quote(
                strike=54900.0,
                option_type=OptionType.CALL,
                timestamp=timestamp,
            ),
            make_quote(
                strike=55000.0,
                option_type=OptionType.CALL,
                timestamp=timestamp,
            ),
            make_quote(
                strike=55100.0,
                option_type=OptionType.CALL,
                timestamp=timestamp,
            ),
        ),
    )

    result = HistoricalOptionContractResolver().resolve(
        selector(
            option_type=OptionType.CALL,
            strike_selection=StrikeSelection.ITM,
        ),
        chain,
        as_of=timestamp,
    )

    assert result.instrument.strike == 55000.0


def test_otm_call_selects_lowest_strike_above_underlying() -> None:
    timestamp = datetime(2026, 9, 9, 10, 0, tzinfo=UTC)
    chain = make_chain(
        underlying_price=55025.0,
        quotes=(
            make_quote(
                strike=54900.0,
                option_type=OptionType.CALL,
                timestamp=timestamp,
            ),
            make_quote(
                strike=55000.0,
                option_type=OptionType.CALL,
                timestamp=timestamp,
            ),
            make_quote(
                strike=55100.0,
                option_type=OptionType.CALL,
                timestamp=timestamp,
            ),
        ),
    )

    result = HistoricalOptionContractResolver().resolve(
        selector(
            option_type=OptionType.CALL,
            strike_selection=StrikeSelection.OTM,
        ),
        chain,
        as_of=timestamp,
    )

    assert result.instrument.strike == 55100.0


def test_itm_put_selects_highest_strike_below_or_equal_to_boundary() -> None:
    timestamp = datetime(2026, 9, 9, 10, 0, tzinfo=UTC)
    chain = make_chain(
        underlying_price=55025.0,
        quotes=(
            make_quote(
                strike=54900.0,
                option_type=OptionType.PUT,
                timestamp=timestamp,
            ),
            make_quote(
                strike=55000.0,
                option_type=OptionType.PUT,
                timestamp=timestamp,
            ),
            make_quote(
                strike=55100.0,
                option_type=OptionType.PUT,
                timestamp=timestamp,
            ),
        ),
    )

    result = HistoricalOptionContractResolver().resolve(
        selector(
            option_type=OptionType.PUT,
            strike_selection=StrikeSelection.ITM,
        ),
        chain,
        as_of=timestamp,
    )

    assert result.instrument.strike == 55100.0


def test_otm_put_selects_highest_strike_below_underlying() -> None:
    timestamp = datetime(2026, 9, 9, 10, 0, tzinfo=UTC)
    chain = make_chain(
        underlying_price=55025.0,
        quotes=(
            make_quote(
                strike=54900.0,
                option_type=OptionType.PUT,
                timestamp=timestamp,
            ),
            make_quote(
                strike=55000.0,
                option_type=OptionType.PUT,
                timestamp=timestamp,
            ),
            make_quote(
                strike=55100.0,
                option_type=OptionType.PUT,
                timestamp=timestamp,
            ),
        ),
    )

    result = HistoricalOptionContractResolver().resolve(
        selector(
            option_type=OptionType.PUT,
            strike_selection=StrikeSelection.OTM,
        ),
        chain,
        as_of=timestamp,
    )

    assert result.instrument.strike == 55000.0


def test_resolver_rejects_future_as_of_relative_to_chain() -> None:
    chain_timestamp = datetime(2026, 9, 9, 10, 0, tzinfo=UTC)
    as_of = datetime(2026, 9, 9, 9, 59, tzinfo=UTC)

    chain = make_chain(
        quotes=(
            make_quote(
                strike=55000.0,
                option_type=OptionType.CALL,
                timestamp=chain_timestamp,
            ),
        ),
        timestamp=chain_timestamp,
    )

    with pytest.raises(ValueError, match="chain snapshot is after as_of"):
        HistoricalOptionContractResolver().resolve(
            selector(),
            chain,
            as_of=as_of,
        )


def test_resolver_rejects_offset_until_semantics_are_defined() -> None:
    timestamp = datetime(2026, 9, 9, 10, 0, tzinfo=UTC)

    chain = make_chain(
        quotes=(
            make_quote(
                strike=55000.0,
                option_type=OptionType.CALL,
                timestamp=timestamp,
            ),
        )
    )

    offset_selector = OptionSelector(
        underlying="BANKNIFTY",
        option_type=OptionType.CALL,
        strike_selection=StrikeSelection.OFFSET,
        strike_offset=1,
    )

    with pytest.raises(NotImplementedError, match="OFFSET"):
        HistoricalOptionContractResolver().resolve(
            offset_selector,
            chain,
            as_of=timestamp,
        )


def test_exact_expiry_unavailable_is_rejected() -> None:
    timestamp = datetime(2026, 9, 9, 10, 0, tzinfo=UTC)
    chain = make_chain(
        quotes=(
            make_quote(
                strike=55000.0,
                option_type=OptionType.CALL,
                expiry="2026-09-24",
                timestamp=timestamp,
            ),
        ),
    )

    with pytest.raises(ValueError, match="exact expiry is not available"):
        HistoricalOptionContractResolver().resolve(
            selector(
                expiry_selection=ExpirySelection.EXACT,
                expiry="2026-10-01",
            ),
            chain,
            as_of=timestamp,
        )


def test_exact_strike_unavailable_is_rejected() -> None:
    timestamp = datetime(2026, 9, 9, 10, 0, tzinfo=UTC)
    chain = make_chain(
        quotes=(
            make_quote(
                strike=55000.0,
                option_type=OptionType.CALL,
                timestamp=timestamp,
            ),
        ),
    )

    with pytest.raises(ValueError, match="exact strike is not available"):
        HistoricalOptionContractResolver().resolve(
            selector(
                strike_selection=StrikeSelection.EXACT,
                strike=55100.0,
            ),
            chain,
            as_of=timestamp,
        )


def test_missing_option_type_is_rejected() -> None:
    timestamp = datetime(2026, 9, 9, 10, 0, tzinfo=UTC)
    chain = make_chain(
        quotes=(
            make_quote(
                strike=55000.0,
                option_type=OptionType.CALL,
                timestamp=timestamp,
            ),
        ),
    )

    with pytest.raises(ValueError, match="option type"):
        HistoricalOptionContractResolver().resolve(
            selector(option_type=OptionType.PUT),
            chain,
            as_of=timestamp,
        )


def test_atm_tie_breaks_to_lower_strike_deterministically() -> None:
    timestamp = datetime(2026, 9, 9, 10, 0, tzinfo=UTC)
    chain = make_chain(
        underlying_price=55050.0,
        quotes=(
            make_quote(
                strike=55000.0,
                option_type=OptionType.CALL,
                timestamp=timestamp,
            ),
            make_quote(
                strike=55100.0,
                option_type=OptionType.CALL,
                timestamp=timestamp,
            ),
        ),
    )

    result = HistoricalOptionContractResolver().resolve(
        selector(),
        chain,
        as_of=timestamp,
    )

    assert result.instrument.strike == 55000.0


def test_naive_as_of_is_rejected() -> None:
    timestamp = datetime(2026, 9, 9, 10, 0, tzinfo=UTC)
    chain = make_chain(
        quotes=(
            make_quote(
                strike=55000.0,
                option_type=OptionType.CALL,
                timestamp=timestamp,
            ),
        ),
    )

    with pytest.raises(ValueError, match="as_of must be timezone-aware"):
        HistoricalOptionContractResolver().resolve(
            selector(),
            chain,
            as_of=datetime(2026, 9, 9, 10, 0),
        )


def test_no_itm_call_strike_is_rejected() -> None:
    timestamp = datetime(2026, 9, 9, 10, 0, tzinfo=UTC)
    chain = make_chain(
        underlying_price=55025.0,
        quotes=(
            make_quote(
                strike=55100.0,
                option_type=OptionType.CALL,
                timestamp=timestamp,
            ),
        ),
    )

    with pytest.raises(ValueError, match="No ITM call strike"):
        HistoricalOptionContractResolver().resolve(
            selector(
                strike_selection=StrikeSelection.ITM,
            ),
            chain,
            as_of=timestamp,
        )


def test_current_week_selects_first_available_future_expiry() -> None:
    timestamp = datetime(2026, 9, 9, 10, 0, tzinfo=UTC)

    chain = make_chain(
        quotes=(
            make_quote(
                strike=55000.0,
                option_type=OptionType.CALL,
                expiry="2026-09-10",
                timestamp=timestamp,
            ),
            make_quote(
                strike=55000.0,
                option_type=OptionType.CALL,
                expiry="2026-09-17",
                timestamp=timestamp,
            ),
            make_quote(
                strike=55000.0,
                option_type=OptionType.CALL,
                expiry="2026-09-24",
                timestamp=timestamp,
            ),
        ),
    )

    result = HistoricalOptionContractResolver().resolve(
        selector(expiry_selection=ExpirySelection.CURRENT_WEEK),
        chain,
        as_of=timestamp,
    )

    assert result.instrument.expiry == "2026-09-10"


def test_next_week_selects_second_available_future_expiry() -> None:
    timestamp = datetime(2026, 9, 9, 10, 0, tzinfo=UTC)

    chain = make_chain(
        quotes=(
            make_quote(
                strike=55000.0,
                option_type=OptionType.CALL,
                expiry="2026-09-10",
                timestamp=timestamp,
            ),
            make_quote(
                strike=55000.0,
                option_type=OptionType.CALL,
                expiry="2026-09-17",
                timestamp=timestamp,
            ),
            make_quote(
                strike=55000.0,
                option_type=OptionType.CALL,
                expiry="2026-09-24",
                timestamp=timestamp,
            ),
        ),
    )

    result = HistoricalOptionContractResolver().resolve(
        selector(expiry_selection=ExpirySelection.NEXT_WEEK),
        chain,
        as_of=timestamp,
    )

    assert result.instrument.expiry == "2026-09-17"


def test_current_month_selects_first_available_expiry_in_current_month() -> None:
    timestamp = datetime(2026, 9, 9, 10, 0, tzinfo=UTC)

    chain = make_chain(
        quotes=(
            make_quote(
                strike=55000.0,
                option_type=OptionType.CALL,
                expiry="2026-09-10",
                timestamp=timestamp,
            ),
            make_quote(
                strike=55000.0,
                option_type=OptionType.CALL,
                expiry="2026-09-24",
                timestamp=timestamp,
            ),
            make_quote(
                strike=55000.0,
                option_type=OptionType.CALL,
                expiry="2026-10-01",
                timestamp=timestamp,
            ),
        ),
    )

    result = HistoricalOptionContractResolver().resolve(
        selector(expiry_selection=ExpirySelection.CURRENT_MONTH),
        chain,
        as_of=timestamp,
    )

    assert result.instrument.expiry == "2026-09-10"


def test_next_month_selects_first_available_expiry_in_next_month() -> None:
    timestamp = datetime(2026, 9, 9, 10, 0, tzinfo=UTC)

    chain = make_chain(
        quotes=(
            make_quote(
                strike=55000.0,
                option_type=OptionType.CALL,
                expiry="2026-09-24",
                timestamp=timestamp,
            ),
            make_quote(
                strike=55000.0,
                option_type=OptionType.CALL,
                expiry="2026-10-01",
                timestamp=timestamp,
            ),
            make_quote(
                strike=55000.0,
                option_type=OptionType.CALL,
                expiry="2026-10-29",
                timestamp=timestamp,
            ),
            make_quote(
                strike=55000.0,
                option_type=OptionType.CALL,
                expiry="2026-11-05",
                timestamp=timestamp,
            ),
        ),
    )

    result = HistoricalOptionContractResolver().resolve(
        selector(expiry_selection=ExpirySelection.NEXT_MONTH),
        chain,
        as_of=timestamp,
    )

    assert result.instrument.expiry == "2026-10-01"
