import pytest

from private_quant_terminal.portfolio.efficient_frontier import (
    FrontierPortfolio,
    evaluate_portfolio,
    evaluate_portfolios,
    maximum_return_portfolio,
    maximum_return_to_volatility_portfolio,
    minimum_volatility_portfolio,
)


class TestFrontierPortfolio:
    def test_calculates_return_to_volatility(self) -> None:
        portfolio = FrontierPortfolio(
            weights=(0.50, 0.50),
            expected_return=0.12,
            volatility=0.20,
        )

        assert portfolio.return_to_volatility == pytest.approx(0.60)

    def test_rejects_zero_volatility_for_ratio(self) -> None:
        portfolio = FrontierPortfolio(
            weights=(1.0,),
            expected_return=0.10,
            volatility=0.0,
        )

        with pytest.raises(
            ValueError,
            match=(
                "Return-to-volatility ratio is undefined "
                "when volatility is zero"
            ),
        ):
            _ = portfolio.return_to_volatility


class TestEfficientFrontier:
    def test_evaluates_portfolio(self) -> None:
        result = evaluate_portfolio(
            weights=(0.50, 0.50),
            expected_returns=(0.10, 0.20),
            covariance_matrix=(
                (0.04, 0.01),
                (0.01, 0.09),
            ),
        )

        assert result.weights == (0.50, 0.50)
        assert result.expected_return == pytest.approx(0.15)
        assert result.volatility == pytest.approx(
            0.1936491673
        )

    def test_evaluates_multiple_portfolios(self) -> None:
        result = evaluate_portfolios(
            candidate_weights=(
                (1.0, 0.0),
                (0.50, 0.50),
                (0.0, 1.0),
            ),
            expected_returns=(0.10, 0.20),
            covariance_matrix=(
                (0.04, 0.01),
                (0.01, 0.09),
            ),
        )

        assert len(result) == 3

        assert result[0].expected_return == pytest.approx(0.10)
        assert result[1].expected_return == pytest.approx(0.15)
        assert result[2].expected_return == pytest.approx(0.20)

    def test_rejects_empty_candidate_portfolios(self) -> None:
        with pytest.raises(
            ValueError,
            match="At least one candidate portfolio is required",
        ):
            evaluate_portfolios(
                candidate_weights=(),
                expected_returns=(0.10, 0.20),
                covariance_matrix=(
                    (0.04, 0.01),
                    (0.01, 0.09),
                ),
            )

    def test_finds_minimum_volatility_portfolio(self) -> None:
        portfolios = (
            FrontierPortfolio(
                weights=(1.0, 0.0),
                expected_return=0.10,
                volatility=0.20,
            ),
            FrontierPortfolio(
                weights=(0.50, 0.50),
                expected_return=0.15,
                volatility=0.15,
            ),
            FrontierPortfolio(
                weights=(0.0, 1.0),
                expected_return=0.20,
                volatility=0.30,
            ),
        )

        result = minimum_volatility_portfolio(portfolios)

        assert result == portfolios[1]

    def test_finds_maximum_return_portfolio(self) -> None:
        portfolios = (
            FrontierPortfolio(
                weights=(1.0, 0.0),
                expected_return=0.10,
                volatility=0.20,
            ),
            FrontierPortfolio(
                weights=(0.50, 0.50),
                expected_return=0.15,
                volatility=0.15,
            ),
            FrontierPortfolio(
                weights=(0.0, 1.0),
                expected_return=0.20,
                volatility=0.30,
            ),
        )

        result = maximum_return_portfolio(portfolios)

        assert result == portfolios[2]

    def test_finds_maximum_return_to_volatility_portfolio(
        self,
    ) -> None:
        portfolios = (
            FrontierPortfolio(
                weights=(1.0, 0.0),
                expected_return=0.10,
                volatility=0.20,
            ),
            FrontierPortfolio(
                weights=(0.50, 0.50),
                expected_return=0.15,
                volatility=0.15,
            ),
            FrontierPortfolio(
                weights=(0.0, 1.0),
                expected_return=0.20,
                volatility=0.30,
            ),
        )

        result = maximum_return_to_volatility_portfolio(
            portfolios
        )

        assert result == portfolios[1]

    def test_rejects_empty_portfolios_for_minimum_volatility(
        self,
    ) -> None:
        with pytest.raises(
            ValueError,
            match="At least one portfolio is required",
        ):
            minimum_volatility_portfolio(())

    def test_rejects_empty_portfolios_for_maximum_return(
        self,
    ) -> None:
        with pytest.raises(
            ValueError,
            match="At least one portfolio is required",
        ):
            maximum_return_portfolio(())

    def test_rejects_empty_portfolios_for_maximum_ratio(
        self,
    ) -> None:
        with pytest.raises(
            ValueError,
            match="At least one portfolio is required",
        ):
            maximum_return_to_volatility_portfolio(())