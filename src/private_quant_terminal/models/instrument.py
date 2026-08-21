from dataclasses import dataclass
from enum import Enum


class InstrumentType(str, Enum):
    EQUITY = "EQUITY"
    INDEX = "INDEX"
    FUTURE = "FUTURE"
    OPTION = "OPTION"


class OptionType(str, Enum):
    CALL = "CE"
    PUT = "PE"


@dataclass(frozen=True)
class Instrument:
    symbol: str
    exchange: str
    instrument_type: InstrumentType
    expiry: str | None = None
    strike: float | None = None
    option_type: OptionType | None = None

    @property
    def identifier(self) -> str:
        parts = [
            self.exchange,
            self.symbol,
            self.instrument_type.value,
        ]

        if self.expiry:
            parts.append(self.expiry)

        if self.strike is not None:
            parts.append(str(self.strike))

        if self.option_type:
            parts.append(self.option_type.value)

        return ":".join(parts)
