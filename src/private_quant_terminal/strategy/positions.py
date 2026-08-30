from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from private_quant_terminal.strategy.options import OptionQuantity, OptionSelector


class LegInstrumentType(str, Enum):
    """Instrument classes that a strategy leg may trade."""

    EQUITY = "EQUITY"
    INDEX = "INDEX"
    FUTURE = "FUTURE"
    OPTION = "OPTION"


class LegAction(str, Enum):
    """Opening transaction direction for a strategy leg."""

    BUY = "BUY"
    SELL = "SELL"


@dataclass(frozen=True)
class StrategyLeg:
    """One executable leg of a strategy position."""

    action: LegAction
    instrument_type: LegInstrumentType
    symbol: str | None = None
    option: OptionSelector | None = None
    quantity: OptionQuantity | None = None

    def __post_init__(self) -> None:
        if self.instrument_type is LegInstrumentType.OPTION:
            if self.option is None:
                raise ValueError(
                    "OPTION legs require an option selector."
                )

        elif self.option is not None:
            raise ValueError(
                "Only OPTION legs may define an option selector."
            )

        if self.instrument_type is not LegInstrumentType.OPTION:
            normalized_symbol = (self.symbol or "").strip().upper()

            if not normalized_symbol:
                raise ValueError(
                    "Non-option legs require a symbol."
                )

            object.__setattr__(self, "symbol", normalized_symbol)


@dataclass(frozen=True)
class PositionGroup:
    """A coordinated group of strategy legs."""

    group_id: str
    name: str
    legs: tuple[StrategyLeg, ...]

    def __post_init__(self) -> None:
        if not self.group_id.strip():
            raise ValueError("Position group ID must not be empty.")

        if not self.name.strip():
            raise ValueError("Position group name must not be empty.")

        if not self.legs:
            raise ValueError(
                "Position group must contain at least one leg."
            )

        object.__setattr__(
            self,
            "group_id",
            self.group_id.strip(),
        )
        object.__setattr__(
            self,
            "name",
            self.name.strip(),
        )
