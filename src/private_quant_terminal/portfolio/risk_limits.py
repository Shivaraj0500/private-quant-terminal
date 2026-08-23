from dataclasses import dataclass


@dataclass(frozen=True)
class PortfolioRiskLimits:
    """Maximum permitted portfolio-level risk exposures."""

    max_gross_exposure: float
    max_net_exposure: float
    max_long_exposure: float
    max_short_exposure: float
    max_largest_position_weight: float

    def __post_init__(self) -> None:
        self._validate_non_negative(
            value=self.max_gross_exposure,
            name="max_gross_exposure",
        )
        self._validate_non_negative(
            value=self.max_net_exposure,
            name="max_net_exposure",
        )
        self._validate_non_negative(
            value=self.max_long_exposure,
            name="max_long_exposure",
        )
        self._validate_non_negative(
            value=self.max_short_exposure,
            name="max_short_exposure",
        )

        if not 0.0 <= self.max_largest_position_weight <= 1.0:
            raise ValueError(
                "max_largest_position_weight must be between zero and one"
            )

    @staticmethod
    def _validate_non_negative(
        value: float,
        name: str,
    ) -> None:
        if value < 0:
            raise ValueError(
                f"{name} must be greater than or equal to zero"
            )
