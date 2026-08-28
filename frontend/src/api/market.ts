import { apiClient } from "./client";

export interface MarketQuoteResponse {
  symbol: string;
  exchange: string;
  timestamp: string;
  last_price: number;
  open: number | null;
  high: number | null;
  low: number | null;
  previous_close: number | null;
  volume: number | null;
}

export interface CandleResponse {
  timestamp: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export async function getLatestQuote(
  symbol: string,
): Promise<MarketQuoteResponse> {
  const response = await apiClient.get<MarketQuoteResponse>(
    `/market-data/${encodeURIComponent(symbol)}/quote`,
  );

  return response.data;
}

export async function getCandles(
  symbol: string,
  limit?: number,
): Promise<CandleResponse[]> {
  const response = await apiClient.get<CandleResponse[]>(
    `/market-data/${encodeURIComponent(symbol)}/candles`,
    {
      params: limit !== undefined ? { limit } : undefined,
    },
  );

  return response.data;
}

export async function getMarketQuotes(
  symbols: string[],
): Promise<MarketQuoteResponse[]> {
  return Promise.all(
    symbols.map((symbol) => getLatestQuote(symbol)),
  );
}
