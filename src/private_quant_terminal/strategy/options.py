from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class OptionType(str, Enum):
    """Option contract type."""

    CALL = "CE"
    PUT = "PE"


class StrikeSelection(str, Enum):
    """How a strategy selects an option strike."""

    ATM = "ATM"
    ITM = "ITM"
    OTM = "OTM"
    EXACT = "EXACT"
    OFFSET = "OFFSET"


class ExpirySelection(str, Enum):
    """How a strategy selects an option expiry."""

    CURRENT_WEEK = "CURRENT_WEEK"
    NEXT_WEEK = "NEXT_WEEK"
    CURRENT_MONTH = "CURRENT_MONTH"
    NEXT_MONTH = "NEXT_MONTH"
    EXACT = "EXACT"


@dataclass(frozen=True)
class OptionSelector:
    """Declarative selector for a concrete option contract."""

    underlying: str
    option_type: OptionType
    strike_selection: StrikeSelection
    strike: float | None = None
    strike_offset: int | None = None
    expiry_selection: ExpirySelection = ExpirySelection.CURRENT_WEEK
    expiry: str | None = None

    def __post_init__(self) -> None:
        underlying = self.underlying.strip().upper()

        if not underlying:
            raise ValueError("Option underlying must not be empty.")

        object.__setattr__(self, "underlying", underlying)

        if self.strike_selection is StrikeSelection.EXACT:
            if self.strike is None:
                raise ValueError(
                    "EXACT strike selection requires a strike."
                )

        elif self.strike_selection is StrikeSelection.OFFSET:
            if self.strike_offset is None:
                raise ValueError(
                    "OFFSET strike selection requires a strike offset."
                )

        elif self.strike is not None or self.strike_offset is not None:
            raise ValueError(
                f"{self.strike_selection.value} strike selection "
                "cannot define strike or strike_offset."
            )

        if self.expiry_selection is ExpirySelection.EXACT:
            if not self.expiry:
                raise ValueError(
                    "EXACT expiry selection requires an expiry."
                )

        elif self.expiry:
            raise ValueError(
                f"{self.expiry_selection.value} expiry selection "
                "cannot define an exact expiry."
            )


@dataclass(frozen=True)
class OptionQuantity:
    """Declarative option quantity."""

    value: int
    unit: str = "LOTS"

    def __post_init__(self) -> None:
        if self.value <= 0:
            raise ValueError("Option quantity must be greater than zero.")

        normalized_unit = self.unit.strip().upper()

        if not normalized_unit:
            raise ValueError("Option quantity unit must not be empty.")

        object.__setattr__(self, "unit", normalized_unit)
