from datetime import UTC, datetime

from private_quant_terminal.models.instrument import Instrument, InstrumentType, OptionType
from private_quant_terminal.research.option_diagnostics import (
    ResearchOptionDiagnosticsCalculator,
)
from private_quant_terminal.research.simulation import ResearchFill, ResearchFillSide
from private_quant_terminal.strategy.actions import ActionType


def _option(
    *,
    symbol="TEST",
    expiry="2026-09-24",
    strike=100.0,
    option_type=OptionType.CALL,
):
    return Instrument(
        symbol=symbol,
        exchange="NSE",
        instrument_type=InstrumentType.OPTION,
        expiry=expiry,
        strike=strike,
        option_type=option_type,
    )


def _fill(
    *,
    timestamp,
    group_id,
    instrument,
    side,
    quantity,
    price,
    action_type,
    transaction_cost=0.0,
):
    return ResearchFill(
        timestamp=timestamp,
        group_id=group_id,
        instrument=instrument,
        side=side,
        quantity=quantity,
        price=price,
        transaction_cost=transaction_cost,
        action_type=action_type,
    )


def test_empty_option_evidence_is_explicit():
    result = ResearchOptionDiagnosticsCalculator().calculate(())

    assert result.option_fill_count == 0
    assert result.option_trade_count == 0
    assert result.option_net_pnl == 0.0
    assert result.trades == ()


def test_long_call_option_trade_is_calculated():
    instrument = _option()
    entry_time = datetime(2026, 9, 20, 10, 0, tzinfo=UTC)
    exit_time = datetime(2026, 9, 20, 11, 0, tzinfo=UTC)

    fills = (
        _fill(
            timestamp=entry_time,
            group_id="call-long",
            instrument=instrument,
            side=ResearchFillSide.BUY,
            quantity=2,
            price=10,
            action_type=ActionType.ENTER,
            transaction_cost=1,
        ),
        _fill(
            timestamp=exit_time,
            group_id="call-long",
            instrument=instrument,
            side=ResearchFillSide.SELL,
            quantity=2,
            price=14,
            action_type=ActionType.EXIT,
            transaction_cost=1,
        ),
    )

    result = ResearchOptionDiagnosticsCalculator().calculate(fills)

    assert result.option_fill_count == 2
    assert result.option_trade_count == 1
    assert result.call_trade_count == 1
    assert result.put_trade_count == 0
    assert result.winning_option_trade_count == 1
    assert result.option_net_pnl == 6.0
    assert result.average_option_trade == 6.0
    assert result.strike_distribution == ((100.0, 1),)
    assert result.expiry_distribution == (("2026-09-24", 1),)


def test_short_put_option_trade_is_calculated():
    instrument = _option(
        expiry="2026-10-01",
        strike=95,
        option_type=OptionType.PUT,
    )
    entry_time = datetime(2026, 9, 20, 10, 0, tzinfo=UTC)
    exit_time = datetime(2026, 9, 21, 11, 0, tzinfo=UTC)

    fills = (
        _fill(
            timestamp=entry_time,
            group_id="put-short",
            instrument=instrument,
            side=ResearchFillSide.SELL,
            quantity=1,
            price=12,
            action_type=ActionType.ENTER,
        ),
        _fill(
            timestamp=exit_time,
            group_id="put-short",
            instrument=instrument,
            side=ResearchFillSide.BUY,
            quantity=1,
            price=7,
            action_type=ActionType.EXIT,
        ),
    )

    result = ResearchOptionDiagnosticsCalculator().calculate(fills)

    assert result.put_trade_count == 1
    assert result.winning_option_trade_count == 1
    assert result.option_net_pnl == 5.0
    assert result.pre_expiry_trade_count == 1
    assert result.expiry_day_trade_count == 0


def test_expiry_day_trade_is_identified_from_entry_date():
    instrument = _option(expiry="2026-09-24")
    entry_time = datetime(2026, 9, 24, 10, 0, tzinfo=UTC)
    exit_time = datetime(2026, 9, 24, 12, 0, tzinfo=UTC)

    fills = (
        _fill(
            timestamp=entry_time,
            group_id="expiry-day",
            instrument=instrument,
            side=ResearchFillSide.SELL,
            quantity=1,
            price=10,
            action_type=ActionType.ENTER,
        ),
        _fill(
            timestamp=exit_time,
            group_id="expiry-day",
            instrument=instrument,
            side=ResearchFillSide.BUY,
            quantity=1,
            price=4,
            action_type=ActionType.EXIT,
        ),
    )

    result = ResearchOptionDiagnosticsCalculator().calculate(fills)

    assert result.expiry_day_trade_count == 1
    assert result.expiry_day_net_pnl == 6.0
    assert result.pre_expiry_trade_count == 0


def test_unmatched_option_fills_are_not_invented_into_trades():
    instrument = _option()

    fills = (
        _fill(
            timestamp=datetime(2026, 9, 20, 10, 0, tzinfo=UTC),
            group_id="unmatched",
            instrument=instrument,
            side=ResearchFillSide.BUY,
            quantity=1,
            price=10,
            action_type=ActionType.ENTER,
        ),
    )

    result = ResearchOptionDiagnosticsCalculator().calculate(fills)

    assert result.option_fill_count == 1
    assert result.option_trade_count == 0
    assert result.option_net_pnl == 0.0
    assert result.trades == ()


def test_multi_leg_straddle_preserves_group_and_leg_evidence():
    call = _option(
        strike=100,
        option_type=OptionType.CALL,
    )
    put = _option(
        strike=100,
        option_type=OptionType.PUT,
    )

    entry_time = datetime(2026, 9, 20, 10, 0, tzinfo=UTC)
    exit_time = datetime(2026, 9, 20, 12, 0, tzinfo=UTC)

    fills = (
        _fill(
            timestamp=entry_time,
            group_id="straddle",
            instrument=call,
            side=ResearchFillSide.SELL,
            quantity=1,
            price=8,
            action_type=ActionType.ENTER,
        ),
        _fill(
            timestamp=entry_time,
            group_id="straddle",
            instrument=put,
            side=ResearchFillSide.SELL,
            quantity=1,
            price=7,
            action_type=ActionType.ENTER,
        ),
        _fill(
            timestamp=exit_time,
            group_id="straddle",
            instrument=call,
            side=ResearchFillSide.BUY,
            quantity=1,
            price=3,
            action_type=ActionType.EXIT,
        ),
        _fill(
            timestamp=exit_time,
            group_id="straddle",
            instrument=put,
            side=ResearchFillSide.BUY,
            quantity=1,
            price=9,
            action_type=ActionType.EXIT,
        ),
    )

    result = ResearchOptionDiagnosticsCalculator().calculate(fills)

    assert result.option_fill_count == 4
    assert result.option_trade_count == 2
    assert result.call_trade_count == 1
    assert result.put_trade_count == 1
    assert result.option_net_pnl == 3.0
    assert result.average_option_trade == 1.5

    assert {trade.group_id for trade in result.trades} == {"straddle"}
    assert {trade.option_type for trade in result.trades} == {
        OptionType.CALL.value,
        OptionType.PUT.value,
    }


def test_partial_option_exits_are_aggregated_into_one_completed_trade():
    instrument = _option()
    entry_time = datetime(2026, 9, 20, 10, 0, tzinfo=UTC)
    first_exit_time = datetime(2026, 9, 20, 11, 0, tzinfo=UTC)
    final_exit_time = datetime(2026, 9, 20, 12, 0, tzinfo=UTC)

    fills = (
        _fill(
            timestamp=entry_time,
            group_id="partial-exit",
            instrument=instrument,
            side=ResearchFillSide.BUY,
            quantity=100,
            price=10,
            action_type=ActionType.ENTER,
        ),
        _fill(
            timestamp=first_exit_time,
            group_id="partial-exit",
            instrument=instrument,
            side=ResearchFillSide.SELL,
            quantity=40,
            price=14,
            action_type=ActionType.EXIT,
        ),
        _fill(
            timestamp=final_exit_time,
            group_id="partial-exit",
            instrument=instrument,
            side=ResearchFillSide.SELL,
            quantity=60,
            price=12,
            action_type=ActionType.EXIT,
        ),
    )

    result = ResearchOptionDiagnosticsCalculator().calculate(fills)

    assert result.option_fill_count == 3
    assert result.option_trade_count == 1

    trade = result.trades[0]

    assert trade.quantity == 100
    assert trade.entry_price == 10
    assert trade.exit_price == 12.8
    assert trade.net_pnl == 280
    assert trade.holding_time_seconds == 7200
