from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class VariableScope(str, Enum):
    """Scope in which a strategy variable is resolved."""

    MARKET = "MARKET"
    POSITION = "POSITION"
    SESSION = "SESSION"
    STRATEGY = "STRATEGY"


class VariableType(str, Enum):
    """Supported strategy variable value types."""

    NUMBER = "NUMBER"
    BOOLEAN = "BOOLEAN"
    STRING = "STRING"
    DATETIME = "DATETIME"


@dataclass(frozen=True)
class StrategyVariable:
    """User-defined or compiler-defined strategy variable."""

    name: str
    variable_type: VariableType
    scope: VariableScope
    value: object | None = None
    description: str = ""

    def __post_init__(self) -> None:
        name = self.name.strip()

        if not name:
            raise ValueError("Variable name must not be empty.")

        if not name.replace("_", "").isalnum():
            raise ValueError(
                "Variable name may contain only letters, numbers, "
                "and underscores."
            )

        if name[0].isdigit():
            raise ValueError(
                "Variable name must not begin with a number."
            )

        object.__setattr__(self, "name", name)

        if self.variable_type is VariableType.NUMBER:
            if self.value is not None and isinstance(
                self.value,
                bool,
            ):
                raise ValueError(
                    "NUMBER variable cannot contain a boolean."
                )

            if self.value is not None and not isinstance(
                self.value,
                (int, float),
            ):
                raise ValueError(
                    "NUMBER variable requires a numeric value."
                )

        elif self.variable_type is VariableType.BOOLEAN:
            if self.value is not None and not isinstance(
                self.value,
                bool,
            ):
                raise ValueError(
                    "BOOLEAN variable requires a boolean value."
                )

        elif self.variable_type is VariableType.STRING:
            if self.value is not None and not isinstance(
                self.value,
                str,
            ):
                raise ValueError(
                    "STRING variable requires a string value."
                )

        elif self.variable_type is VariableType.DATETIME:
            if self.value is not None and not isinstance(
                self.value,
                datetime,
            ):
                raise ValueError(
                    "DATETIME variable requires a datetime value."
                )


@dataclass(frozen=True)
class MarketContext:
    """Market data available to strategy expressions."""

    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float | None = None

    underlying_price: float | None = None
    option_price: float | None = None

    def __post_init__(self) -> None:
        if self.high < self.low:
            raise ValueError("high cannot be below low.")


@dataclass(frozen=True)
class PositionContext:
    """Current strategy position state."""

    quantity: float = 0.0
    entry_price: float | None = None
    current_price: float | None = None
    average_price: float | None = None

    realized_pnl: float = 0.0
    unrealized_pnl: float = 0.0

    entry_timestamp: datetime | None = None

    @property
    def unrealized_pnl_percent(self) -> float:
        """Return unrealized P&L as a percentage."""

        reference_price = self.average_price or self.entry_price

        if reference_price in (None, 0.0):
            return 0.0

        return (
            self.unrealized_pnl
            / abs(reference_price * self.quantity)
        ) * 100.0


@dataclass(frozen=True)
class SessionContext:
    """Runtime state accumulated during the trading session."""

    current_time: datetime
    entries_today: int = 0
    trades_today: int = 0
    bars_since_entry: int = 0
    minutes_since_entry: float | None = None

    last_entry_time: datetime | None = None
    last_exit_time: datetime | None = None

    def __post_init__(self) -> None:
        if self.entries_today < 0:
            raise ValueError(
                "entries_today cannot be negative."
            )

        if self.trades_today < 0:
            raise ValueError(
                "trades_today cannot be negative."
            )

        if self.bars_since_entry < 0:
            raise ValueError(
                "bars_since_entry cannot be negative."
            )


@dataclass(frozen=True)
class StrategyRuntimeContext:
    """Immutable snapshot used when evaluating strategy rules."""

    market: MarketContext
    position: PositionContext = field(
        default_factory=PositionContext,
    )
    session: SessionContext | None = None

    variables: tuple[StrategyVariable, ...] = ()

    @property
    def is_position_open(self) -> bool:
        return self.position.quantity != 0.0

    @property
    def current_price(self) -> float:
        if self.position.current_price is not None:
            return self.position.current_price

        return self.market.close

    def resolve(self, name: str) -> object:
        """Resolve a variable by its canonical runtime name."""

        normalized = name.strip().lower()

        builtins: dict[str, object] = {
            "open": self.market.open,
            "high": self.market.high,
            "low": self.market.low,
            "close": self.market.close,
            "volume": self.market.volume,
            "timestamp": self.market.timestamp,
            "underlying_price": self.market.underlying_price,
            "option_price": self.market.option_price,
            "position_quantity": self.position.quantity,
            "entry_price": self.position.entry_price,
            "current_price": self.current_price,
            "average_price": self.position.average_price,
            "realized_pnl": self.position.realized_pnl,
            "unrealized_pnl": self.position.unrealized_pnl,
            "unrealized_pnl_percent": (
                self.position.unrealized_pnl_percent
            ),
            "position_open": self.is_position_open,
        }

        if self.session is not None:
            builtins.update(
                {
                    "current_time": self.session.current_time,
                    "entries_today": self.session.entries_today,
                    "trades_today": self.session.trades_today,
                    "bars_since_entry": (
                        self.session.bars_since_entry
                    ),
                    "minutes_since_entry": (
                        self.session.minutes_since_entry
                    ),
                    "last_entry_time": (
                        self.session.last_entry_time
                    ),
                    "last_exit_time": (
                        self.session.last_exit_time
                    ),
                }
            )

        if normalized in builtins:
            return builtins[normalized]

        for variable in self.variables:
            if variable.name.lower() == normalized:
                return variable.value

        raise KeyError(
            f"Unknown strategy runtime variable: {name}"
        )
