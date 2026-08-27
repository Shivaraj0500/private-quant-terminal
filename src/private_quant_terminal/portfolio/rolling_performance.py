from dataclasses import dataclass

from private_quant_terminal.portfolio.rolling_drawdown import (
    rolling_drawdown,
    rolling_max_drawdown,
)
from private_quant_terminal.portfolio.rolling_metrics import (
    rolling_average,
    rolling_returns,
    rolling_volatility,
)


@dataclass(frozen=True)
class PortfolioRollingMetrics:
    """Rolling portfolio analytics calculated over return windows."""

    rolling_returns: tuple[float, ...]
    rolling_average: tuple[float, ...]
    rolling_volatility: tuple[float, ...]
    rolling_drawdown: tuple[float, ...]
    rolling_max_drawdown: tuple[float, ...]


def calculate_rolling_metrics(
    returns: tuple[float, ...],
    window: int,
) -> PortfolioRollingMetrics:
    """Calculate rolling portfolio analytics for a return series."""
    _validate_returns(returns)

    values = _cumulative_values(returns)

    return PortfolioRollingMetrics(
        rolling_returns=rolling_returns(
            returns=returns,
            window=window,
        ),
        rolling_average=rolling_average(
            values=returns,
            window=window,
        ),
        rolling_volatility=rolling_volatility(
            returns=returns,
            window=window,
        ),
        rolling_drawdown=rolling_drawdown(
            values=values,
            window=window,
        ),
        rolling_max_drawdown=rolling_max_drawdown(
            values=values,
            window=window,
        ),
    )


def _cumulative_values(
    returns: tuple[float, ...],
) -> tuple[float, ...]:
    value = 1.0
    values: list[float] = []

    for portfolio_return in returns:
        value *= 1.0 + portfolio_return
        values.append(value)

    return tuple(values)


def _validate_returns(
    returns: tuple[float, ...],
) -> None:
    if not returns:
        raise ValueError("returns must not be empty")

    if any(value <= -1.0 for value in returns):
        raise ValueError("returns must be greater than -1.0")
