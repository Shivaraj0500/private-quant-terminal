import { apiClient } from "./client";

export interface StrategyCondition {
  indicator: string;
  operator: string;
  value: number;
}

export interface PositionSizing {
  method: string;
  value: number;
}

export interface StopLoss {
  type: string;
  value: number | null;
}

export interface TakeProfit {
  type: string;
  value: number | null;
}

export interface ExecutionAssumptions {
  order_type: string;
  slippage_bps: number;
  transaction_cost_bps: number;
}

export interface StrategyCreateRequest {
  strategy_id: string;
  name: string;
  description: string;
  instruments: string[];
  timeframe: string;
  entry_conditions: StrategyCondition[];
  exit_conditions: StrategyCondition[];
  position_sizing: PositionSizing;
  stop_loss: StopLoss;
  take_profit: TakeProfit;
  execution: ExecutionAssumptions;
}

export interface StrategyVersion {
  strategy_id: string;
  version: number;
  strategy_hash: string;
  name: string;
  description: string;
  instruments: string[];
  timeframe: string;
  entry_conditions: StrategyCondition[];
  exit_conditions: StrategyCondition[];
  position_sizing: PositionSizing;
  stop_loss: StopLoss;
  take_profit: TakeProfit;
  execution: ExecutionAssumptions;
  status: string;
  created_at: string;
}

export interface StrategyCreateResponse {
  version: StrategyVersion;
}

export interface StrategyVersionListResponse {
  versions: StrategyVersion[];
}

export async function createStrategy(
  payload: StrategyCreateRequest,
): Promise<StrategyCreateResponse> {
  const response = await apiClient.post<StrategyCreateResponse>(
    "/strategies",
    payload,
  );

  return response.data;
}

export async function getStrategyVersion(
  strategyId: string,
  version: number,
): Promise<StrategyVersion> {
  const response = await apiClient.get<StrategyVersion>(
    `/strategies/${encodeURIComponent(strategyId)}/versions/${version}`,
  );

  return response.data;
}

export async function listStrategies(): Promise<StrategyVersionListResponse> {
  const response = await apiClient.get<StrategyVersionListResponse>(
    "/strategies",
  );

  return response.data;
}

export async function listStrategyVersions(
  strategyId: string,
): Promise<StrategyVersionListResponse> {
  const response = await apiClient.get<StrategyVersionListResponse>(
    `/strategies/${encodeURIComponent(strategyId)}/versions`,
  );

  return response.data;
}
