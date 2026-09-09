from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from private_quant_terminal.models.instrument import InstrumentType, OptionType
from private_quant_terminal.research.simulation import ResearchFill


@dataclass(frozen=True)
class ResearchOptionTradeEvidence:
    group_id: str
    instrument_identifier: str
    option_type: str
    strike: float
    expiry: str
    entry_time: datetime
    exit_time: datetime
    entry_price: float
    exit_price: float
    quantity: float
    net_pnl: float
    holding_time_seconds: float
    expiry_day: bool
    pre_expiry: bool


@dataclass(frozen=True)
class ResearchOptionDiagnostics:
    option_fill_count: int
    option_trade_count: int
    call_trade_count: int
    put_trade_count: int
    winning_option_trade_count: int
    losing_option_trade_count: int
    option_net_pnl: float
    average_option_trade: float
    expiry_day_trade_count: int
    expiry_day_net_pnl: float
    pre_expiry_trade_count: int
    pre_expiry_net_pnl: float
    strike_distribution: tuple[tuple[float, int], ...]
    expiry_distribution: tuple[tuple[str, int], ...]
    trades: tuple[ResearchOptionTradeEvidence, ...]


class ResearchOptionDiagnosticsCalculator:
    """Calculate evidence from concrete historical option fills."""

    def calculate(
        self,
        fills: tuple[ResearchFill, ...],
    ) -> ResearchOptionDiagnostics:
        option_fills = tuple(
            fill
            for fill in fills
            if fill.instrument.instrument_type is InstrumentType.OPTION
        )

        if not option_fills:
            return ResearchOptionDiagnostics(
                option_fill_count=0,
                option_trade_count=0,
                call_trade_count=0,
                put_trade_count=0,
                winning_option_trade_count=0,
                losing_option_trade_count=0,
                option_net_pnl=0.0,
                average_option_trade=0.0,
                expiry_day_trade_count=0,
                expiry_day_net_pnl=0.0,
                pre_expiry_trade_count=0,
                pre_expiry_net_pnl=0.0,
                strike_distribution=(),
                expiry_distribution=(),
                trades=(),
            )

        entries: dict[str, ResearchFill] = {}
        exit_fills: dict[str, list[ResearchFill]] = {}
        completed: list[ResearchOptionTradeEvidence] = []

        for fill in option_fills:
            key = fill.group_id + "|" + fill.instrument.identifier

            if fill.action_type.name == "ENTER":
                entries[key] = fill
                exit_fills[key] = []
                continue

            if fill.action_type.name != "EXIT":
                continue

            if key not in entries:
                continue

            entry = entries[key]
            exits = exit_fills[key]
            exits.append(fill)

            total_exit_quantity = sum(
                exit_fill.quantity for exit_fill in exits
            )

            if total_exit_quantity < entry.quantity:
                continue

            instrument = entry.instrument
            if instrument.expiry is None or instrument.strike is None:
                continue
            if instrument.option_type is None:
                continue

            closing_exits = tuple(exits)
            closing_quantity = entry.quantity

            direction = 1.0 if entry.side.value == "BUY" else -1.0

            gross_pnl = sum(
                (
                    exit_fill.price - entry.price
                )
                * exit_fill.quantity
                * direction
                for exit_fill in closing_exits
            )

            transaction_cost = entry.transaction_cost + sum(
                exit_fill.transaction_cost
                for exit_fill in closing_exits
            )

            net_pnl = gross_pnl - transaction_cost

            weighted_exit_price = sum(
                exit_fill.price * exit_fill.quantity
                for exit_fill in closing_exits
            ) / closing_quantity

            final_exit = closing_exits[-1]

            holding_seconds = (
                final_exit.timestamp - entry.timestamp
            ).total_seconds()

            expiry_date = datetime.fromisoformat(
                instrument.expiry
            ).date()

            expiry_day = entry.timestamp.date() == expiry_date
            pre_expiry = entry.timestamp.date() < expiry_date

            completed.append(
                ResearchOptionTradeEvidence(
                    group_id=entry.group_id,
                    instrument_identifier=instrument.identifier,
                    option_type=instrument.option_type.value,
                    strike=float(instrument.strike),
                    expiry=instrument.expiry,
                    entry_time=entry.timestamp,
                    exit_time=final_exit.timestamp,
                    entry_price=entry.price,
                    exit_price=weighted_exit_price,
                    quantity=closing_quantity,
                    net_pnl=net_pnl,
                    holding_time_seconds=holding_seconds,
                    expiry_day=expiry_day,
                    pre_expiry=pre_expiry,
                )
            )

            del entries[key]
            del exit_fills[key]

        trades = tuple(completed)

        call_count = sum(
            trade.option_type == OptionType.CALL.value
            for trade in trades
        )
        put_count = sum(
            trade.option_type == OptionType.PUT.value
            for trade in trades
        )

        option_net_pnl = sum(trade.net_pnl for trade in trades)

        strike_counts: dict[float, int] = {}
        expiry_counts: dict[str, int] = {}

        for trade in trades:
            strike_counts[trade.strike] = (
                strike_counts.get(trade.strike, 0) + 1
            )
            expiry_counts[trade.expiry] = (
                expiry_counts.get(trade.expiry, 0) + 1
            )

        expiry_day_trades = tuple(
            trade for trade in trades if trade.expiry_day
        )
        pre_expiry_trades = tuple(
            trade for trade in trades if trade.pre_expiry
        )

        return ResearchOptionDiagnostics(
            option_fill_count=len(option_fills),
            option_trade_count=len(trades),
            call_trade_count=call_count,
            put_trade_count=put_count,
            winning_option_trade_count=sum(
                trade.net_pnl > 0 for trade in trades
            ),
            losing_option_trade_count=sum(
                trade.net_pnl < 0 for trade in trades
            ),
            option_net_pnl=option_net_pnl,
            average_option_trade=(
                option_net_pnl / len(trades) if trades else 0.0
            ),
            expiry_day_trade_count=len(expiry_day_trades),
            expiry_day_net_pnl=sum(
                trade.net_pnl for trade in expiry_day_trades
            ),
            pre_expiry_trade_count=len(pre_expiry_trades),
            pre_expiry_net_pnl=sum(
                trade.net_pnl for trade in pre_expiry_trades
            ),
            strike_distribution=tuple(sorted(strike_counts.items())),
            expiry_distribution=tuple(sorted(expiry_counts.items())),
            trades=trades,
        )
