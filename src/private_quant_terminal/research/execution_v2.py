from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from private_quant_terminal.models import Candle
from private_quant_terminal.models.instrument import Instrument, InstrumentType
from private_quant_terminal.strategy.actions import EnterAction, ExitAction
from private_quant_terminal.strategy.compiler import CompiledStrategyPlan
from private_quant_terminal.strategy.rule_evaluator import (
    RuleEvaluationResult,
    StrategyRuleEvaluator,
)
from private_quant_terminal.strategy.variables import (
    PositionContext,
    SessionContext,
    StrategyRuntimeContext,
)
from private_quant_terminal.strategy.positions import PositionGroup
from private_quant_terminal.research.position_book import ResearchPositionBook
from private_quant_terminal.research.simulation import (
    ResearchActionEvent,
    ResearchFill,
    ResearchSimulationAdapter,
    ResearchSimulationStep,
)


@dataclass(frozen=True)
class ResearchV2ExecutionRequest:
    plan: CompiledStrategyPlan
    candles: Sequence[Candle]
    initial_equity: float = 0.0
    run_id: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.plan, CompiledStrategyPlan):
            raise TypeError(
                "ResearchV2ExecutionRequest.plan must be a CompiledStrategyPlan."
            )
        if not self.candles:
            raise ValueError("ResearchV2ExecutionRequest requires candles.")
        if self.initial_equity < 0:
            raise ValueError("initial_equity cannot be negative.")


@dataclass(frozen=True)
class ResearchV2ExecutionResult:
    run_id: str | None
    strategy_id: str
    strategy_version: int
    strategy_hash: str
    simulation_steps: tuple[ResearchSimulationStep, ...]
    action_events: tuple[ResearchActionEvent, ...]
    fills: tuple[ResearchFill, ...]
    equity_curve: tuple[tuple[object, float], ...]
    final_equity: float
    realized_pnl: float
    unrealized_pnl: float
    transaction_cost: float


class ResearchV2Executor:
    """Execute a compiled canonical strategy over historical candles.

    Strategy semantics remain owned by the canonical rule evaluator.
    This component owns only the historical iteration boundary and the
    economic simulation/accounting boundary.
    """

    def __init__(self, *, initial_equity: float = 0.0) -> None:
        if initial_equity < 0:
            raise ValueError("initial_equity cannot be negative.")
        self.initial_equity = initial_equity

    def execute(
        self,
        request: ResearchV2ExecutionRequest,
    ) -> ResearchV2ExecutionResult:
        if not isinstance(request, ResearchV2ExecutionRequest):
            raise TypeError(
                "ResearchV2Executor.execute() requires a "
                "ResearchV2ExecutionRequest."
            )

        plan = request.plan
        candles = request.candles

        evaluator = StrategyRuleEvaluator()
        adapter = ResearchSimulationAdapter()

        position_book = ResearchPositionBook()
        position_context = PositionContext()
        session = SessionContext(current_time=candles[0].timestamp)

        simulation_steps: list[ResearchSimulationStep] = []
        action_events: list[ResearchActionEvent] = []
        fills: list[ResearchFill] = []
        equity_curve: list[tuple[object, float]] = []

        realized_pnl = 0.0
        transaction_cost = 0.0
        equity = request.initial_equity

        for index, candle in enumerate(candles):
            session = SessionContext(
                current_time=candle.timestamp,
                entries_today=session.entries_today,
                trades_today=session.trades_today,
                bars_since_entry=session.bars_since_entry,
                minutes_since_entry=session.minutes_since_entry,
                last_entry_time=session.last_entry_time,
                last_exit_time=session.last_exit_time,
            )

            market = self._market_context(candle)
            runtime_context = StrategyRuntimeContext(
                market=market,
                position=position_context,
                session=session,
                variables=plan.variables,
            )

            evaluation: RuleEvaluationResult = evaluator.evaluate(
                plan.rules,
                candles,
                index,
                context=runtime_context,
            )

            step_events: list[ResearchActionEvent] = []
            step_fills: list[ResearchFill] = []

            for action in evaluation.actions:
                action_type = action.action_type

                if action_type.name == "ENTER":
                    if position_book.positions_for_group(action.position.group_id):
                        continue

                    for leg in action.position.legs:
                        if leg.instrument_type.name == "OPTION":
                            raise NotImplementedError(
                                "Historical option execution belongs to Phase 9."
                            )

                        instrument_type = {
                            "EQUITY": InstrumentType.EQUITY,
                            "INDEX": InstrumentType.INDEX,
                            "FUTURE": InstrumentType.FUTURE,
                        }.get(leg.instrument_type.name)

                        if instrument_type is None:
                            raise NotImplementedError(
                                f"Historical execution for {leg.instrument_type.name} "
                                "legs belongs to a later research gate."
                            )

                        instrument = Instrument(
                            symbol=leg.symbol,
                            exchange="RESEARCH",
                            instrument_type=instrument_type,
                        )

                        if not isinstance(action, EnterAction):
                            raise TypeError("ENTER action must be an EnterAction.")

                        event, fill, _ = adapter.enter(
                            timestamp=candle.timestamp,
                            action=EnterAction(
                                position=PositionGroup(
                                    group_id=action.position.group_id,
                                    name=action.position.name,
                                    legs=(leg,),
                                )
                            ),
                            instrument=instrument,
                            price=candle.close,
                            quantity=(
                                1.0
                                if leg.quantity is None
                                else float(leg.quantity)
                            ),
                        )

                        accounting = position_book.apply_fill(fill)
                        realized_pnl += accounting.realized_pnl
                        transaction_cost += accounting.transaction_cost
                        step_events.append(event)
                        step_fills.append(fill)

                elif action_type.name == "EXIT":
                    group_positions = position_book.positions_for_group(action.group_id)

                    for existing_position in group_positions:
                        event, fill, _ = adapter.exit(
                            timestamp=candle.timestamp,
                            action=ExitAction(group_id=action.group_id),
                            position=existing_position,
                            price=candle.close,
                        )

                        accounting = position_book.apply_fill(fill)
                        realized_pnl += accounting.realized_pnl
                        transaction_cost += accounting.transaction_cost
                        step_events.append(event)
                        step_fills.append(fill)

                else:
                    raise NotImplementedError(
                        f"ResearchV2Executor does not yet simulate "
                        f"{action_type.name}; this belongs to a later gate."
                    )

            action_events.extend(step_events)
            fills.extend(step_fills)

            open_positions = position_book.positions()

            unrealized_pnl = sum(
                (candle.close - open_position.average_price)
                * open_position.quantity
                for open_position in open_positions
            )

            if not open_positions:
                position_context = PositionContext(
                    realized_pnl=realized_pnl,
                )
            else:
                net_quantity = sum(
                    open_position.quantity
                    for open_position in open_positions
                )
                weighted_entry = (
                    sum(
                        abs(open_position.quantity)
                        * open_position.average_price
                        for open_position in open_positions
                    )
                    / sum(abs(open_position.quantity) for open_position in open_positions)
                )
                position_context = PositionContext(
                    quantity=net_quantity,
                    entry_price=weighted_entry,
                    current_price=candle.close,
                    average_price=weighted_entry,
                    realized_pnl=realized_pnl,
                    unrealized_pnl=unrealized_pnl,
                )

            equity = (
                request.initial_equity
                + realized_pnl
                + unrealized_pnl
                - transaction_cost
            )

            step = ResearchSimulationStep(
                timestamp=candle.timestamp,
                action_events=tuple(step_events),
                fills=tuple(step_fills),
                positions=position_book.positions(),
                realized_pnl=realized_pnl,
                unrealized_pnl=unrealized_pnl,
                transaction_cost=transaction_cost,
                equity=equity,
            )

            simulation_steps.append(step)
            equity_curve.append((candle.timestamp, equity))

        final_unrealized = (
            simulation_steps[-1].unrealized_pnl
            if simulation_steps
            else 0.0
        )

        return ResearchV2ExecutionResult(
            run_id=request.run_id,
            strategy_id=plan.strategy_id,
            strategy_version=plan.version,
            strategy_hash=plan.strategy_hash,
            simulation_steps=tuple(simulation_steps),
            action_events=tuple(action_events),
            fills=tuple(fills),
            equity_curve=tuple(equity_curve),
            final_equity=equity,
            realized_pnl=realized_pnl,
            unrealized_pnl=final_unrealized,
            transaction_cost=transaction_cost,
        )

    @staticmethod
    def _market_context(candle: Candle):
        from private_quant_terminal.strategy.variables import MarketContext

        return MarketContext(
            timestamp=candle.timestamp,
            open=candle.open,
            high=candle.high,
            low=candle.low,
            close=candle.close,
            volume=candle.volume,
        )
