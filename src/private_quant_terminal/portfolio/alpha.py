def expected_return(
    benchmark_return: float,
    beta_value: float,
    risk_free_rate: float = 0.0,
) -> float:
    """Calculate the CAPM expected portfolio return."""
    return risk_free_rate + (
        beta_value
        * (benchmark_return - risk_free_rate)
    )


def alpha(
    portfolio_return: float,
    benchmark_return: float,
    beta_value: float,
    risk_free_rate: float = 0.0,
) -> float:
    """Calculate Jensen's alpha."""
    return (
        portfolio_return
        - expected_return(
            benchmark_return=benchmark_return,
            beta_value=beta_value,
            risk_free_rate=risk_free_rate,
        )
    )