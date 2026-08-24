from collections.abc import Sequence
from dataclasses import dataclass

from private_quant_terminal.portfolio.optimization import (
    portfolio_expected_return,
    portfolio_volatility,
)


@dataclass(frozen=True)
class FrontierPortfolio:
    """A portfolio evaluated on expected return and volatility."""

    weights: tuple[float, ...]
    expected_return: float
    volatility: float

    @property
    def return_to_volatility(self) -> float:
        """Return the portfolio return-to-volatility ratio."""
        if self.volatility == 0:
            raise ValueError(
                "Return-to-volatility ratio is undefined "
                "when volatility is zero"
            )

        return self.expected_return / self.volatility


def evaluate_portfolio(
    weights: Sequence[float],
    expected_returns: Sequence[float],
    covariance_matrix: Sequence[Sequence[float]],
) -> FrontierPortfolio:
    """Evaluate a portfolio using expected return and volatility."""
    return FrontierPortfolio(
        weights=tuple(weights),
        expected_return=portfolio_expected_return(
            weights,
            expected_returns,
        ),
        volatility=portfolio_volatility(
            weights,
            covariance_matrix,
        ),
    )


def evaluate_portfolios(
    candidate_weights: Sequence[Sequence[float]],
    expected_returns: Sequence[float],
    covariance_matrix: Sequence[Sequence[float]],
) -> tuple[FrontierPortfolio, ...]:
    """Evaluate a collection of candidate portfolios."""
    if not candidate_weights:
        raise ValueError(
            "At least one candidate portfolio is required"
        )

    return tuple(
        evaluate_portfolio(
            weights,
            expected_returns,
            covariance_matrix,
        )
        for weights in candidate_weights
    )


def minimum_volatility_portfolio(
    portfolios: Sequence[FrontierPortfolio],
) -> FrontierPortfolio:
    """Return the portfolio with the lowest volatility."""
    _validate_portfolios(portfolios)

    return min(
        portfolios,
        key=lambda portfolio: portfolio.volatility,
    )


def maximum_return_portfolio(
    portfolios: Sequence[FrontierPortfolio],
) -> FrontierPortfolio:
    """Return the portfolio with the highest expected return."""
    _validate_portfolios(portfolios)

    return max(
        portfolios,
        key=lambda portfolio: portfolio.expected_return,
    )


def maximum_return_to_volatility_portfolio(
    portfolios: Sequence[FrontierPortfolio],
) -> FrontierPortfolio:
    """Return the portfolio with the highest return-to-volatility ratio."""
    _validate_portfolios(portfolios)

    return max(
        portfolios,
        key=lambda portfolio: portfolio.return_to_volatility,
    )


def _validate_portfolios(
    portfolios: Sequence[FrontierPortfolio],
) -> None:
    """Validate that at least one portfolio is available."""
    if not portfolios:
        raise ValueError(
            "At least one portfolio is required"
        )