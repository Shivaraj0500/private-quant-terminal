from dataclasses import dataclass


@dataclass(frozen=True)
class PortfolioRisk:
    """Portfolio-level exposure and concentration metrics."""

    gross_exposure: float
    net_exposure: float
    long_exposure: float
    short_exposure: float
    largest_position_weight: float
    position_count: int

    def __post_init__(self) -> None:
        if self.gross_exposure < 0:
            raise ValueError(
                "gross_exposure must be greater than or equal to zero"
            )

        if self.long_exposure < 0:
            raise ValueError(
                "long_exposure must be greater than or equal to zero"
            )

        if self.short_exposure < 0:
            raise ValueError(
                "short_exposure must be greater than or equal to zero"
            )

        if not 0.0 <= self.largest_position_weight <= 1.0:
            raise ValueError(
                "largest_position_weight must be between zero and one"
            )

        if self.position_count < 0:
            raise ValueError(
                "position_count must be greater than or equal to zero"
            )
