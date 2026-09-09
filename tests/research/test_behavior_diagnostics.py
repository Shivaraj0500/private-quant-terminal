from datetime import UTC, datetime

from private_quant_terminal.research.behavior_diagnostics import (
    ResearchBehaviorDiagnosticsCalculator,
)
from private_quant_terminal.research.execution import ResearchTrade


def make_trade(
    *,
    entry_hour: int,
    exit_hour: int,
    net_pnl: float,
) -> ResearchTrade:
    return ResearchTrade(
        symbol="RELIANCE",
        entry_time=datetime(2026, 1, 1, entry_hour, tzinfo=UTC),
        exit_time=datetime(2026, 1, 1, exit_hour, tzinfo=UTC),
        entry_price=100.0,
        exit_price=100.0,
        quantity=1.0,
        gross_pnl=net_pnl,
        transaction_cost=0.0,
        net_pnl=net_pnl,
    )


def test_calculates_entry_and_exit_hour_distribution() -> None:
    trades = (
        make_trade(entry_hour=9, exit_hour=10, net_pnl=100.0),
        make_trade(entry_hour=9, exit_hour=11, net_pnl=-50.0),
        make_trade(entry_hour=10, exit_hour=12, net_pnl=25.0),
    )

    result = ResearchBehaviorDiagnosticsCalculator().calculate(trades)

    assert result.entry_hour_distribution == ((9, 2), (10, 1))
    assert result.exit_hour_distribution == ((10, 1), (11, 1), (12, 1))


def test_calculates_winner_loser_and_zero_pnl_statistics() -> None:
    trades = (
        make_trade(entry_hour=9, exit_hour=10, net_pnl=100.0),
        make_trade(entry_hour=10, exit_hour=11, net_pnl=-50.0),
        make_trade(entry_hour=11, exit_hour=12, net_pnl=0.0),
        make_trade(entry_hour=12, exit_hour=13, net_pnl=20.0),
    )

    result = ResearchBehaviorDiagnosticsCalculator().calculate(trades)

    assert result.winning_trade_count == 2
    assert result.losing_trade_count == 1
    assert result.zero_pnl_trade_count == 1
    assert result.winning_pnl == 120.0
    assert result.losing_pnl == -50.0
    assert result.average_winning_trade == 60.0
    assert result.average_losing_trade == -50.0


def test_calculates_loss_concentration_by_entry_hour() -> None:
    trades = (
        make_trade(entry_hour=9, exit_hour=10, net_pnl=-100.0),
        make_trade(entry_hour=9, exit_hour=11, net_pnl=-50.0),
        make_trade(entry_hour=10, exit_hour=12, net_pnl=-25.0),
        make_trade(entry_hour=11, exit_hour=13, net_pnl=100.0),
    )

    result = ResearchBehaviorDiagnosticsCalculator().calculate(trades)

    assert result.loss_by_entry_hour == ((9, 150.0), (10, 25.0))


def test_empty_trade_set_returns_zero_diagnostics() -> None:
    result = ResearchBehaviorDiagnosticsCalculator().calculate(())

    assert result.entry_hour_distribution == ()
    assert result.exit_hour_distribution == ()
    assert result.winning_trade_count == 0
    assert result.losing_trade_count == 0
    assert result.zero_pnl_trade_count == 0
    assert result.winning_pnl == 0.0
    assert result.losing_pnl == 0.0
    assert result.average_winning_trade == 0.0
    assert result.average_losing_trade == 0.0
    assert result.loss_by_entry_hour == ()
