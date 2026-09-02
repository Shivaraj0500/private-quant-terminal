from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from private_quant_terminal.models import Candle
from private_quant_terminal.strategy.actions import StrategyAction
from private_quant_terminal.strategy.evaluator import ConditionEvaluator
from private_quant_terminal.strategy.rules import StrategyRule
from private_quant_terminal.strategy.variables import StrategyRuntimeContext


@dataclass(frozen=True)
class TriggeredRule:
    """A strategy rule whose condition evaluated to true."""

    rule_id: str
    actions: tuple[StrategyAction, ...]


@dataclass(frozen=True)
class RuleEvaluationResult:
    """Deterministic result of evaluating strategy rules."""

    triggered_rules: tuple[TriggeredRule, ...]

    @property
    def actions(self) -> tuple[StrategyAction, ...]:
        """Return all actions emitted by triggered rules."""

        return tuple(action for rule in self.triggered_rules for action in rule.actions)


class StrategyRuleEvaluator:
    """Evaluate strategy rules without mutating strategy state."""

    def __init__(
        self,
        condition_evaluator: ConditionEvaluator | None = None,
    ) -> None:
        self._conditions = (
            condition_evaluator if condition_evaluator is not None else ConditionEvaluator()
        )

    def evaluate(
        self,
        rules: Sequence[StrategyRule],
        candles: Sequence[Candle],
        index: int,
        context: StrategyRuntimeContext | None = None,
        current_state: str | None = None,
    ) -> RuleEvaluationResult:
        """Evaluate applicable enabled rules in deterministic priority order."""

        normalized_state = (
            current_state.strip()
            if current_state is not None
            else None
        )

        if normalized_state == "":
            raise ValueError("current_state must not be empty.")

        ordered_rules = sorted(
            (
                rule
                for rule in rules
                if rule.enabled
                and (
                    not rule.states
                    or normalized_state is None
                    or normalized_state in rule.states
                )
            ),
            key=lambda rule: (-rule.priority, rule.rule_id),
        )

        triggered: list[TriggeredRule] = []

        for rule in ordered_rules:
            if self._conditions.evaluate(
                rule.condition,
                candles,
                index,
                context,
            ):
                triggered.append(
                    TriggeredRule(
                        rule_id=rule.rule_id,
                        actions=rule.actions,
                    )
                )

        return RuleEvaluationResult(
            triggered_rules=tuple(triggered),
        )
