import { apiClient } from "./client";

export interface ResearchRunRequest {
  strategy_id: string;
  strategy_version: number;
  symbol: string;
  timeframe: string;
  parameters: Record<string, unknown>;
  initial_equity: number;
}

export interface ResearchRunSummary {
  run_id: string;
  strategy_id: string;
  strategy_version: number;
  strategy_hash: string;
  dataset_hash: string;
  symbol: string;
  timeframe: string;
  start_time: string;
  end_time: string;
  parameters: Record<string, unknown>;
  parameters_hash: string;
  status: string;
  created_at: string;
}

export interface ResearchTrade {
  symbol: string;
  entry_time: string;
  exit_time: string;
  entry_price: number;
  exit_price: number;
  quantity: number;
  gross_pnl: number;
  transaction_cost: number;
  net_pnl: number;
}

export interface ResearchEvent {
  timestamp: string;
  event_type: string;
  symbol: string;
  price: number;
  quantity: number;
}

export interface ResearchPerformance {
  realized_pnl: number;
  unrealized_pnl: number;
  total_pnl: number;
  winning_trades: number;
  losing_trades: number;
  win_rate: number;
  average_win: number;
  average_loss: number;
  profit_factor: number;
  returns: number[];
  max_drawdown: number;
  max_drawdown_percent: number;
  sharpe_ratio: number;
  sortino_ratio: number;
  downside_deviation: number;
  calmar_ratio: number;
}

export interface ResearchExecution {
  run_id: string;
  events: ResearchEvent[];
  trades: ResearchTrade[];
  equity_curve: number[];
  final_equity: number;
}

export interface ResearchRunResponse {
  run: ResearchRunSummary;
  execution: ResearchExecution;
  performance: ResearchPerformance;
}

export async function executeResearchRun(
  payload: ResearchRunRequest,
): Promise<ResearchRunResponse> {
  const response = await apiClient.post<ResearchRunResponse>(
    "/research/runs",
    payload,
  );

  return response.data;
}

export async function getResearchRun(
  runId: string,
): Promise<ResearchRunSummary> {
  const response = await apiClient.get<ResearchRunSummary>(
    `/research/runs/${encodeURIComponent(runId)}`,
  );

  return response.data;
}
