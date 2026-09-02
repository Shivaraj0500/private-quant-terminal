from __future__ import annotations

from private_quant_terminal.strategy.actions import EnterAction, ExitAction
from private_quant_terminal.strategy.conditions import all_of, compare
from private_quant_terminal.strategy.expressions import constant, indicator
from private_quant_terminal.strategy.ir import StrategyDefinition, StrategyIR
from private_quant_terminal.strategy.positions import (
    LegAction,
    LegInstrumentType,
    PositionGroup,
    StrategyLeg,
)
from private_quant_terminal.strategy.rules import StrategyRule


def strategy_definition_to_ir(
    strategy: StrategyDefinition,
    *,
    version: int,
) -> StrategyIR:
    """Convert a legacy StrategyDefinition into the canonical StrategyIR."""

    if version <= 0:
        raise ValueError("Strategy version must be greater than zero.")

    position_group = PositionGroup(
        group_id="legacy-position",
        name="Legacy Strategy Position",
        legs=tuple(
            StrategyLeg(
                action=LegAction.BUY,
                instrument_type=LegInstrumentType.EQUITY,
                symbol=instrument,
            )
            for instrument in strategy.instruments
        ),
    )

    entry_conditions = tuple(
        compare(
            indicator(condition.indicator),
            condition.operator.value,
            constant(condition.value),
        )
        for condition in strategy.entry_conditions
    )

    exit_conditions = tuple(
        compare(
            indicator(condition.indicator),
            condition.operator.value,
            constant(condition.value),
        )
        for condition in strategy.exit_conditions
    )

    rules = (
        StrategyRule(
            rule_id="legacy-entry",
            name="Legacy Entry",
            condition=all_of(*entry_conditions),
            actions=(EnterAction(position=position_group),),
        ),
        StrategyRule(
            rule_id="legacy-exit",
            name="Legacy Exit",
            condition=all_of(*exit_conditions),
            actions=(ExitAction(group_id=position_group.group_id),),
        ),
    )

    return StrategyIR(
        strategy_id=strategy.strategy_id,
        name=strategy.name,
        description=strategy.description,
        version=version,
        status=strategy.status,
        instruments=strategy.instruments,
        timeframe=strategy.timeframe,
        rules=rules,
        position_groups=(position_group,),
        position_sizing=strategy.position_sizing,
        stop_loss=strategy.stop_loss,
        take_profit=strategy.take_profit,
        execution=strategy.execution,
    )
