import type {
  Condition,
  ExecutionAssumptions,
  PositionGroup,
  PositionSizing,
  StopLoss,
  StrategyIR,
  StrategyRule,
  TakeProfit,
} from "../types";
import type {
  StrategyCondition,
  StrategyCreateRequest,
} from "../../../api/strategy";

function conditionToIR(condition: StrategyCondition): Condition {
  return {
    left: {
      type: "INDICATOR",
      indicator: condition.indicator,
    },
    operator: condition.operator as
      | ">"
      | ">="
      | "<"
      | "<="
      | "=="
      | "!=",
    right: {
      type: "VALUE",
      value: condition.value,
    },
  };
}

function buildRules(
  form: StrategyCreateRequest,
  positionGroup: PositionGroup,
): StrategyRule[] {
  const rules: StrategyRule[] = [];

  if (form.entry_conditions.length > 0) {
    rules.push({
      rule_id: "legacy-entry",
      condition:
        form.entry_conditions.length === 1
          ? conditionToIR(form.entry_conditions[0])
          : {
              operator: "AND",
              conditions: form.entry_conditions.map(conditionToIR),
            },
      actions: [
        {
          type: "ENTER",
          position_group: positionGroup,
        },
      ],
    });
  }

  if (form.exit_conditions.length > 0) {
    rules.push({
      rule_id: "legacy-exit",
      condition:
        form.exit_conditions.length === 1
          ? conditionToIR(form.exit_conditions[0])
          : {
              operator: "AND",
              conditions: form.exit_conditions.map(conditionToIR),
            },
      actions: [
        {
          type: "EXIT",
          group_id: positionGroup.group_id,
        },
      ],
    });
  }

  return rules;
}

function buildLegacyPositionGroup(
  form: StrategyCreateRequest,
): PositionGroup {
  return {
    group_id: "legacy-position",
    name: "Legacy Strategy Position",
    legs: form.instruments.map((instrument) => ({
      instrument_type: "EQUITY" as const,
      symbol: instrument.trim().toUpperCase(),
      action: "BUY" as const,
    })),
  };
}

function mapPositionSizing(
  value: StrategyCreateRequest["position_sizing"],
): PositionSizing {
  return {
    method: value.method,
    value: value.value,
  };
}

function mapStopLoss(
  value: StrategyCreateRequest["stop_loss"],
): StopLoss {
  return {
    type: value.type,
    value: value.value,
  };
}

function mapTakeProfit(
  value: StrategyCreateRequest["take_profit"],
): TakeProfit {
  return {
    type: value.type,
    value: value.value,
  };
}

function mapExecution(
  value: StrategyCreateRequest["execution"],
): ExecutionAssumptions {
  return {
    order_type: value.order_type,
    slippage_bps: value.slippage_bps,
    transaction_cost_bps: value.transaction_cost_bps,
  };
}

export function legacyStrategyToIR(
  form: StrategyCreateRequest,
): StrategyIR {
  const positionGroup = buildLegacyPositionGroup(form);

  return {
    strategy_id: form.strategy_id.trim(),
    name: form.name.trim(),
    description: form.description.trim(),
    version: 1,
    status: "DRAFT",

    instruments: form.instruments
      .map((instrument) => instrument.trim().toUpperCase())
      .filter(Boolean),

    timeframe: form.timeframe,

    variables: [],

    rules: buildRules(form, positionGroup),

    states: [],

    transitions: [],

    data_requirements: [],

    position_groups: [positionGroup],

    position_sizing: mapPositionSizing(form.position_sizing),

    stop_loss: mapStopLoss(form.stop_loss),

    take_profit: mapTakeProfit(form.take_profit),

    execution: mapExecution(form.execution),
  };
}
