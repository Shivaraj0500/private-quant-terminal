export type StrategyStatus =
  | "DRAFT"
  | "VALIDATED"
  | "RESEARCH"
  | "PAPER"
  | "LIVE"
  | "PAUSED"
  | "STOPPED"
  | string;

export type VariableType =
  | "NUMBER"
  | "BOOLEAN"
  | "STRING"
  | "DATETIME";

export type VariableScope =
  | "MARKET"
  | "POSITION"
  | "SESSION"
  | "STRATEGY";

export type LegInstrumentType =
  | "EQUITY"
  | "INDEX"
  | "FUTURE"
  | "OPTION";

export type LegAction =
  | "BUY"
  | "SELL";

export type ActionType =
  | "ENTER"
  | "EXIT"
  | "MODIFY"
  | "ROLL"
  | "HEDGE";

export type ExpressionType =
  | "VALUE"
  | "PRICE"
  | "INDICATOR"
  | "VARIABLE"
  | "POSITION_PROPERTY"
  | "TIME"
  | "CROSS_ABOVE"
  | "CROSS_BELOW"
  | "ADD"
  | "SUBTRACT"
  | "MULTIPLY"
  | "DIVIDE";

export type LogicalOperator =
  | "AND"
  | "OR"
  | "NOT";

export type ComparisonOperator =
  | ">"
  | ">="
  | "<"
  | "<="
  | "=="
  | "!=";

export interface StrategyMetadata {
  strategy_id: string;
  name: string;
  description: string;
  version: number;
  status: StrategyStatus;
}

export interface StrategyIdentity {
  strategy_id: string;
  version: number;
  strategy_hash?: string;
}

export interface StrategyVariable {
  name: string;
  type: VariableType;
  scope: VariableScope;
  value?: number | boolean | string | null;
}

export interface IndicatorDefinition {
  name: string;
  type: string;
  parameters?: Record<string, number | string | boolean>;
}

export interface Expression {
  type: ExpressionType;

  value?: number | string | boolean;

  symbol?: string;

  indicator?: string;

  variable?: string;

  position_property?: string;

  time_field?: string;

  left?: Expression;

  right?: Expression;

  operand?: Expression;

  parameters?: Record<string, number | string | boolean>;
}

export interface LogicalCondition {
  operator: LogicalOperator;

  conditions?: Condition[];

  operand?: Condition;
}

export interface ComparisonCondition {
  left: Expression;
  operator: ComparisonOperator;
  right: Expression;
}

export type Condition =
  | ComparisonCondition
  | LogicalCondition;

export interface VariableAssignment {
  variable: string;
  expression: Expression;
}

export interface VariableMutation {
  variable: string;
  expression: Expression;
}

export interface PositionLeg {
  instrument_type: LegInstrumentType;
  symbol?: string;
  action: LegAction;
  quantity?: number;

  option_type?: "CALL" | "PUT";

  strike?: number | string;

  expiry?: string;
}

export interface PositionGroup {
  group_id: string;
  name: string;
  legs: PositionLeg[];
}

export interface EnterAction {
  type: "ENTER";
  position_group: PositionGroup;
}

export interface ExitAction {
  type: "EXIT";
  group_id: string;
}

export interface ModifyAction {
  type: "MODIFY";
  group_id: string;
  changes: Record<string, Expression>;
}

export interface RollAction {
  type: "ROLL";
  group_id: string;
  replacement: PositionGroup;
}

export interface HedgeAction {
  type: "HEDGE";
  group_id: string;
  hedge: PositionGroup;
}

export type StrategyAction =
  | EnterAction
  | ExitAction
  | ModifyAction
  | RollAction
  | HedgeAction;

export interface StrategyRule {
  rule_id: string;
  condition: Condition;
  actions: StrategyAction[];

  states?: string[];

  priority?: number;

  enabled?: boolean;

  assignments?: VariableAssignment[];

  mutations?: VariableMutation[];
}

export interface StrategyState {
  state_id: string;
  name: string;
  initial?: boolean;
  terminal?: boolean;
}

export interface StateTransition {
  transition_id: string;
  from_state: string;
  to_state: string;
  condition: Condition;
  actions: StrategyAction[];

  priority?: number;

  enabled?: boolean;
}

export interface SessionRules {
  mode?: "INTRADAY" | "OVERNIGHT";
  start_time?: string;
  end_time?: string;
  expiry_day_only?: boolean;
}

export interface PositionSizing {
  method: string;
  value: number;
}

export interface StopLoss {
  type: string;
  value?: number | null;
}

export interface TakeProfit {
  type: string;
  value?: number | null;
}

export interface ExecutionAssumptions {
  order_type?: string;
  slippage_bps?: number;
  transaction_cost_bps?: number;
  assumptions?: Record<string, unknown>;
}

export interface DataRequirement {
  requirement_id: string;
  source?: string;
  symbol?: string;
  timeframe?: string;
  fields?: string[];
  parameters?: Record<string, unknown>;
}

export interface StrategyIR {
  strategy_id: string;
  name: string;
  description: string;
  version: number;
  status: StrategyStatus;

  instruments: string[];

  timeframe: string;

  variables: StrategyVariable[];

  rules: StrategyRule[];

  states: StrategyState[];

  transitions: StateTransition[];

  data_requirements: DataRequirement[];

  position_groups: PositionGroup[];

  session?: SessionRules;

  position_sizing?: PositionSizing;

  stop_loss?: StopLoss;

  take_profit?: TakeProfit;

  execution: ExecutionAssumptions;
}
