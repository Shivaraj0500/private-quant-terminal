from dataclasses import dataclass


@dataclass(frozen=True)
class RiskResult:
    """Result of validating an order against risk rules."""

    approved: bool
    reason: str | None = None

    def __post_init__(self) -> None:
        if self.approved and self.reason is not None:
            raise ValueError(
                "approved risk results cannot include a rejection reason"
            )

        if not self.approved and not self.reason:
            raise ValueError(
                "rejected risk results must include a reason"
            )
