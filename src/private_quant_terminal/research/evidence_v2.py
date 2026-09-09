from __future__ import annotations

from dataclasses import dataclass

from private_quant_terminal.research.execution import (
    ResearchEquityPoint,
    ResearchExecutionEvent,
    ResearchExecutionEventType,
    ResearchExecutionResult,
    ResearchTrade,
)
from private_quant_terminal.research.execution_v2 import ResearchV2ExecutionResult
from private_quant_terminal.research.simulation import (
    ResearchActionEvent,
    ResearchFill,
    ResearchFillSide,
)


@dataclass(frozen=True)
class ResearchV2EvidenceAdapter:
    """Translate supported V2 simulation evidence into legacy research evidence.

    This adapter does not evaluate strategy conditions or change economic
    semantics. It only translates the supported single-leg ENTER/EXIT
    evidence into the existing research evidence contract.
    """

    def adapt(
        self,
        execution: ResearchV2ExecutionResult,
    ) -> ResearchExecutionResult:
        if not isinstance(execution, ResearchV2ExecutionResult):
            raise TypeError(
                "ResearchV2EvidenceAdapter.adapt() requires a "
                "ResearchV2ExecutionResult."
            )

        if not execution.run_id or not execution.run_id.strip():
            raise ValueError(
                "V2 execution must contain a run_id before evidence adaptation."
            )

        fills = execution.fills
        action_events = execution.action_events

        if len(fills) != len(action_events):
            raise ValueError(
                "V2 action event and fill counts must match for evidence adaptation."
            )

        events: list[ResearchExecutionEvent] = []
        trades: list[ResearchTrade] = []

        open_fill: ResearchFill | None = None

        for action_event, fill in zip(action_events, fills):
            self._validate_event_alignment(action_event, fill)

            if fill.action_type.name == "ENTER":
                if open_fill is not None:
                    raise ValueError(
                        "Unsupported overlapping ENTER actions in V2 evidence."
                    )

                events.append(
                    ResearchExecutionEvent(
                        timestamp=fill.timestamp,
                        event_type=ResearchExecutionEventType.ENTRY,
                        symbol=fill.instrument.symbol,
                        price=fill.price,
                        quantity=fill.quantity,
                    )
                )
                open_fill = fill

            elif fill.action_type.name == "EXIT":
                if open_fill is None:
                    raise ValueError(
                        "EXIT evidence has no corresponding open ENTER fill."
                    )

                if fill.group_id != open_fill.group_id:
                    raise ValueError(
                        "EXIT evidence group does not match the open ENTER group."
                    )

                if fill.instrument.identifier != open_fill.instrument.identifier:
                    raise ValueError(
                        "EXIT evidence instrument does not match the open ENTER instrument."
                    )

                events.append(
                    ResearchExecutionEvent(
                        timestamp=fill.timestamp,
                        event_type=ResearchExecutionEventType.EXIT,
                        symbol=fill.instrument.symbol,
                        price=fill.price,
                        quantity=fill.quantity,
                    )
                )

                trades.append(self._build_trade(open_fill, fill))
                open_fill = None

            else:
                raise ValueError(
                    f"Unsupported V2 action type for legacy evidence: "
                    f"{fill.action_type.name}."
                )

        if open_fill is not None:
            raise ValueError(
                "V2 research evidence requires all positions to be closed "
                "before legacy evidence adaptation."
            )

        equity_curve = tuple(
            ResearchEquityPoint(
                timestamp=timestamp,
                equity=float(equity),
            )
            for timestamp, equity in execution.equity_curve
        )

        return ResearchExecutionResult(
            run_id=execution.run_id,
            events=tuple(events),
            trades=tuple(trades),
            equity_curve=equity_curve,
            final_equity=execution.final_equity,
        )

    @staticmethod
    def _validate_event_alignment(
        action_event: ResearchActionEvent,
        fill: ResearchFill,
    ) -> None:
        if action_event.timestamp != fill.timestamp:
            raise ValueError(
                "V2 action event timestamp does not match its fill timestamp."
            )

        if action_event.group_id != fill.group_id:
            raise ValueError(
                "V2 action event group does not match its fill group."
            )

        if action_event.action_type is not fill.action_type:
            raise ValueError(
                "V2 action event type does not match its fill action type."
            )

    @staticmethod
    def _build_trade(
        entry: ResearchFill,
        exit: ResearchFill,
    ) -> ResearchTrade:
        if entry.quantity != exit.quantity:
            raise ValueError(
                "Legacy ResearchTrade requires matching entry and exit quantities."
            )

        if entry.side is ResearchFillSide.BUY:
            gross_pnl = (
                exit.price - entry.price
            ) * entry.quantity
        elif entry.side is ResearchFillSide.SELL:
            gross_pnl = (
                entry.price - exit.price
            ) * entry.quantity
        else:
            raise ValueError(
                f"Unsupported entry fill side: {entry.side!r}."
            )

        transaction_cost = (
            entry.transaction_cost + exit.transaction_cost
        )

        return ResearchTrade(
            symbol=entry.instrument.symbol,
            entry_time=entry.timestamp,
            exit_time=exit.timestamp,
            entry_price=entry.price,
            exit_price=exit.price,
            quantity=entry.quantity,
            gross_pnl=gross_pnl,
            transaction_cost=transaction_cost,
            net_pnl=gross_pnl - transaction_cost,
        )
