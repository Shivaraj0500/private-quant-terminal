from datetime import UTC, datetime, timedelta

from private_quant_terminal.research.execution import ResearchTrade
from private_quant_terminal.research.trade_analytics import (
    ResearchTradeAnalyticsCalculator,
)


def make_trade(
    *,
    entry_day: int,
    exit_day: int,
    net_pnl: float,
) -> ResearchTrade:
    return ResearchTrade(
        symbol="RELIANCE",
        entry_time=datetime(
            2026,
            1,
            entry_day,
            tzinfo=UTC,
        ),
        exit_time=datetime(
            2026,
            1,
            exit_day,
            tzinfo=UTC,
        ),
        entry_price=100.0,
        exit_price=100.0,
        quantity=10.0,
        gross_pnl=net_pnl,
        transaction_cost=0.0,
        net_pnl=net_pnl,
    )


def test_calculates_basic_trade_analytics() -> None:
    trades = (
        make_trade(entry_day=1, exit_day=2, net_pnl=100.0),
        make_trade(entry_day=3, exit_day=5, net_pnl=-50.0),
        make_trade(entry_day=6, exit_day=10, net_pnl=25.0),
    )

    result = ResearchTradeAnalyticsCalculator().calculate(trades)

    assert result.total_trades == 3
    assert result.average_trade == 25.0
    assert result.best_trade == 100.0
    assert result.worst_trade == -50.0


def test_calculates_holding_time_analytics() -> None:
    trades = (
        make_trade(entry_day=1, exit_day=2, net_pnl=10.0),
        make_trade(entry_day=3, exit_day=5, net_pnl=-5.0),
        make_trade(entry_day=6, exit_day=10, net_pnl=20.0),
    )

    result = ResearchTradeAnalyticsCalculator().calculate(trades)

    assert result.shortest_holding_time == timedelta(days=1)
    assert result.longest_holding_time == timedelta(days=4)
    assert result.average_holding_time == timedelta(days=7 / 3)


def test_calculates_consecutive_win_and_loss_streaks() -> None:
    trades = (
        make_trade(entry_day=1, exit_day=2, net_pnl=10.0),
        make_trade(entry_day=3, exit_day=4, net_pnl=20.0),
        make_trade(entry_day=5, exit_day=6, net_pnl=-5.0),
        make_trade(entry_day=7, exit_day=8, net_pnl=-10.0),
        make_trade(entry_day=9, exit_day=10, net_pnl=-15.0),
        make_trade(entry_day=11, exit_day=12, net_pnl=5.0),
    )

    result = ResearchTradeAnalyticsCalculator().calculate(trades)

    assert result.max_consecutive_wins == 2
    assert result.max_consecutive_losses == 3


def test_zero_pnl_breaks_both_streaks() -> None:
    trades = (
        make_trade(entry_day=1, exit_day=2, net_pnl=10.0),
        make_trade(entry_day=3, exit_day=4, net_pnl=0.0),
        make_trade(entry_day=5, exit_day=6, net_pnl=20.0),
        make_trade(entry_day=7, exit_day=8, net_pnl=-5.0),
        make_trade(entry_day=9, exit_day=10, net_pnl=0.0),
        make_trade(entry_day=11, exit_day=12, net_pnl=-10.0),
    )

    result = ResearchTradeAnalyticsCalculator().calculate(trades)

    assert result.max_consecutive_wins == 1
    assert result.max_consecutive_losses == 1


def test_empty_trade_set_returns_zero_analytics() -> None:
    result = ResearchTradeAnalyticsCalculator().calculate(())

    assert result.total_trades == 0
    assert result.average_trade == 0.0
    assert result.best_trade == 0.0
    assert result.worst_trade == 0.0
    assert result.average_holding_time == timedelta(0)
    assert result.shortest_holding_time == timedelta(0)
    assert result.longest_holding_time == timedelta(0)
    assert result.max_consecutive_wins == 0
    assert result.max_consecutive_losses == 0
