from private_quant_terminal.research.evaluator import (
    StrategyDecision,
    evaluate_strategy,
)
from private_quant_terminal.research.execution import (
    ResearchExecutionEvent,
    ResearchExecutionEventType,
    ResearchExecutionRequest,
    ResearchExecutionResult,
    ResearchTrade,
)
from private_quant_terminal.research.indicators import calculate_indicators
from private_quant_terminal.strategy import (
    PositionSizingMethod,
    StrategyVersion,
)


class ResearchExecutor:
    """Deterministic bar-by-bar executor for strategy research."""

    def __init__(self, initial_equity: float) -> None:
        if initial_equity < 0:
            raise ValueError("initial_equity cannot be negative")

        self._initial_equity = initial_equity

    def execute(
        self,
        request: ResearchExecutionRequest,
    ) -> ResearchExecutionResult:
        """Execute a research run deterministically over candle data."""

        self._validate_request(request)

        strategy = request.strategy_version.specification
        self._validate_position_sizing(strategy_version=request.strategy_version)

        events: list[ResearchExecutionEvent] = []
        trades: list[ResearchTrade] = []

        position_quantity = 0.0
        entry_price: float | None = None
        entry_time = None

        for candle in request.candles:
            indicator_names = self._indicator_names(strategy)
            indicator_values = calculate_indicators(
                indicator_names,
                request.candles[: request.candles.index(candle) + 1],
            )

            decision = evaluate_strategy(
                strategy,
                indicator_values,
            )

            if (
                decision is StrategyDecision.ENTRY
                and position_quantity == 0.0
            ):
                quantity = strategy.position_sizing.value
                execution_price = self._entry_price(
                    candle.close,
                    strategy.execution.slippage_bps,
                )

                position_quantity = quantity
                entry_price = execution_price
                entry_time = candle.timestamp

                events.append(
                    ResearchExecutionEvent(
                        timestamp=candle.timestamp,
                        event_type=ResearchExecutionEventType.ENTRY,
                        symbol=request.run.symbol,
                        price=execution_price,
                        quantity=quantity,
                    )
                )

            elif (
                decision is StrategyDecision.EXIT
                and position_quantity > 0.0
                and entry_price is not None
                and entry_time is not None
            ):
                execution_price = self._exit_price(
                    candle.close,
                    strategy.execution.slippage_bps,
                )

                gross_pnl = (
                    execution_price - entry_price
                ) * position_quantity

                transaction_cost = self._transaction_cost(
                    entry_price=entry_price,
                    exit_price=execution_price,
                    quantity=position_quantity,
                    transaction_cost_bps=(
                        strategy.execution.transaction_cost_bps
                    ),
                )

                net_pnl = gross_pnl - transaction_cost

                events.append(
                    ResearchExecutionEvent(
                        timestamp=candle.timestamp,
                        event_type=ResearchExecutionEventType.EXIT,
                        symbol=request.run.symbol,
                        price=execution_price,
                        quantity=position_quantity,
                    )
                )

                trades.append(
                    ResearchTrade(
                        symbol=request.run.symbol,
                        entry_time=entry_time,
                        exit_time=candle.timestamp,
                        entry_price=entry_price,
                        exit_price=execution_price,
                        quantity=position_quantity,
                        gross_pnl=gross_pnl,
                        transaction_cost=transaction_cost,
                        net_pnl=net_pnl,
                    )
                )

                position_quantity = 0.0
                entry_price = None
                entry_time = None

        final_equity = self._initial_equity + sum(
            trade.net_pnl
            for trade in trades
        )

        return ResearchExecutionResult(
            run_id=request.run.run_id,
            events=tuple(events),
            trades=tuple(trades),
            final_equity=final_equity,
        )

    @staticmethod
    def _validate_request(
        request: ResearchExecutionRequest,
    ) -> None:
        if request.run.run_id == "":
            raise ValueError("research run ID cannot be empty")

        if (
            request.run.strategy_id
            != request.strategy_version.strategy_id
        ):
            raise ValueError(
                "strategy identity does not match"
            )

        if (
            request.run.strategy_version
            != request.strategy_version.version
        ):
            raise ValueError(
                "strategy version does not match"
            )

        if (
            request.strategy_version.specification.strategy_id
            != request.strategy_version.strategy_id
        ):
            raise ValueError(
                "strategy identity does not match"
            )

    @staticmethod
    def _validate_position_sizing(
        *,
        strategy_version: StrategyVersion,
    ) -> None:
        method = (
            strategy_version.specification.position_sizing.method
        )

        if method is not PositionSizingMethod.FIXED_QUANTITY:
            raise ValueError(
                "Unsupported research position sizing method: "
                f"{method.value}"
            )

    @staticmethod
    def _indicator_names(strategy) -> tuple[str, ...]:
        names = {
            condition.indicator
            for condition in (
                strategy.entry_conditions
                + strategy.exit_conditions
            )
        }

        return tuple(sorted(names))

    @staticmethod
    def _entry_price(
        close: float,
        slippage_bps: float,
    ) -> float:
        return close * (1.0 + slippage_bps / 10000.0)

    @staticmethod
    def _exit_price(
        close: float,
        slippage_bps: float,
    ) -> float:
        return close * (1.0 - slippage_bps / 10000.0)

    @staticmethod
    def _transaction_cost(
        *,
        entry_price: float,
        exit_price: float,
        quantity: float,
        transaction_cost_bps: float,
    ) -> float:
        notional = (
            entry_price * quantity
            + exit_price * quantity
        )

        return notional * transaction_cost_bps / 10000.0
